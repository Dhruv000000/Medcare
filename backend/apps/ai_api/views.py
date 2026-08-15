from __future__ import annotations

import logging

from django.core.exceptions import RequestDataTooBig
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import UserRateThrottle
from rest_framework.exceptions import ParseError, ValidationError as DRFValidationError

from apps.accounts.permissions import IsPatient
from apps.ai_audit.models import AiPredictionEvent
from apps.ai_audit.services import record_prediction_event

from .chat_service import ChatServiceError, ChatServiceUnavailableError, get_symptom_chat_reply
from .constants import ACADEMIC_DISCLAIMER, MAX_REQUEST_BYTES, MODEL_VERSION
from .permissions import IsAiInferenceUser
from .serializers import (
    HeartRiskPredictionRequestSerializer,
    HeartRiskPredictionResponseSerializer,
    SymptomChatRequestSerializer,
)
from .services import ModelUnavailableError, PredictionServiceError, predict

logger = logging.getLogger(__name__)

SYMPTOM_CHAT_DISCLAIMER = (
    "This AI assistant provides general health information only. It is not a "
    "diagnosis or medical advice. Consult a qualified healthcare professional for "
    "any medical concerns, and seek emergency care for severe or worsening symptoms."
)


class AiInferenceThrottle(UserRateThrottle):
    scope = "ai_inference"


class HeartRiskPredictionView(APIView):
    """Stateless inference boundary around the fixed Phase 17 academic artifact."""

    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated, IsAiInferenceUser]
    throttle_classes = [AiInferenceThrottle]
    parser_classes = [JSONParser]

    def post(self, request):
        content_length = request.META.get("CONTENT_LENGTH")
        if content_length:
            try:
                if int(content_length) > MAX_REQUEST_BYTES:
                    return Response(
                        {"detail": "Request body is too large."},
                        status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    )
            except (TypeError, ValueError):
                return Response(
                    {"detail": "Invalid request size."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if request.content_type != "application/json":
            return Response(
                {"detail": "Content-Type must be application/json."},
                status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            )

        try:
            if len(request.body) > MAX_REQUEST_BYTES:
                return Response(
                    {"detail": "Request body is too large."},
                    status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                )
        except RequestDataTooBig:
            return Response(
                {"detail": "Request body is too large."},
                status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            )

        try:
            payload = request.data
        except ParseError:
            return Response(
                {"detail": "Malformed JSON body."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = HeartRiskPredictionRequestSerializer(data=payload)
        try:
            serializer.is_valid(raise_exception=True)
        except DRFValidationError:
            record_prediction_event(request, AiPredictionEvent.Status.VALIDATION_FAILED)
            raise
        try:
            result = predict(serializer.feature_frame())
            response_data = {
                **result,
                "disclaimer": ACADEMIC_DISCLAIMER,
            }
            response_serializer = HeartRiskPredictionResponseSerializer(response_data)
            record_prediction_event(request, AiPredictionEvent.Status.COMPLETED, response_data)
            logger.info(
                "Phase 18 prediction completed: model=%s role=%s success=true",
                MODEL_VERSION,
                request.user.role,
            )
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        except ModelUnavailableError:
            record_prediction_event(request, AiPredictionEvent.Status.MODEL_UNAVAILABLE)
            logger.error(
                "Phase 18 prediction unavailable: model=%s role=%s success=false",
                MODEL_VERSION,
                request.user.role,
            )
            return Response(
                {"detail": "AI prediction service is temporarily unavailable."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except PredictionServiceError:
            record_prediction_event(request, AiPredictionEvent.Status.INFERENCE_FAILED)
            logger.error(
                "Phase 18 prediction failed: model=%s role=%s success=false",
                MODEL_VERSION,
                request.user.role,
            )
            return Response(
                {"detail": "AI prediction could not be completed."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as exc:
            record_prediction_event(request, AiPredictionEvent.Status.INFERENCE_FAILED)
            logger.error(
                "Phase 18 unexpected prediction error: model=%s role=%s exception_type=%s",
                MODEL_VERSION,
                request.user.role,
                type(exc).__name__,
            )
            return Response(
                {"detail": "An unexpected server error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SymptomChatView(APIView):
    """Stateless patient-facing symptom chatbot backed by the Groq chat API."""

    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated, IsPatient]
    throttle_classes = [AiInferenceThrottle]
    parser_classes = [JSONParser]

    def post(self, request):
        if request.content_type != "application/json":
            return Response(
                {"detail": "Content-Type must be application/json."},
                status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            )

        try:
            if len(request.body) > MAX_REQUEST_BYTES:
                return Response(
                    {"detail": "Request body is too large."},
                    status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                )
        except RequestDataTooBig:
            return Response(
                {"detail": "Request body is too large."},
                status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            )

        try:
            payload = request.data
        except ParseError:
            return Response(
                {"detail": "Malformed JSON body."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = SymptomChatRequestSerializer(data=payload)
        serializer.is_valid(raise_exception=True)

        try:
            reply = get_symptom_chat_reply(
                serializer.validated_data["message"],
                serializer.validated_data.get("history", []),
            )
            logger.info("Symptom chat completed: role=%s success=true", request.user.role)
            return Response(
                {"reply": reply, "disclaimer": SYMPTOM_CHAT_DISCLAIMER},
                status=status.HTTP_200_OK,
            )
        except ChatServiceUnavailableError:
            logger.error("Symptom chat unavailable: role=%s success=false", request.user.role)
            return Response(
                {"detail": "The symptom assistant is temporarily unavailable."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except ChatServiceError:
            logger.error("Symptom chat failed: role=%s success=false", request.user.role)
            return Response(
                {"detail": "The symptom assistant could not respond."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
