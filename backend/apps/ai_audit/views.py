from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdministrator
from apps.ai_api.permissions import IsAiInferenceUser

from .models import AiPredictionEvent
from .serializers import AiAuditSummarySerializer, AiPredictionReportSerializer


class DoctorPredictionReportListView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def _doctor_allowed(self, request):
        return bool(request.user.is_active and request.user.role == "doctor")

    def get(self, request):
        if not self._doctor_allowed(request):
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        queryset = AiPredictionEvent.objects.filter(
            requesting_user=request.user,
            status=AiPredictionEvent.Status.COMPLETED,
        )[:100]
        return Response(AiPredictionReportSerializer(queryset, many=True).data)


class DoctorPredictionReportDetailView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, event_id):
        if not request.user.is_active or request.user.role != "doctor":
            return Response({"detail": "Report not found."}, status=status.HTTP_404_NOT_FOUND)
        event = AiPredictionEvent.objects.filter(
            event_id=event_id,
            requesting_user=request.user,
            status=AiPredictionEvent.Status.COMPLETED,
        ).first()
        if event is None:
            return Response({"detail": "Report not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(AiPredictionReportSerializer(event).data)


class AdminAiAuditSummaryView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated, IsAdministrator]

    def get(self, request):
        queryset = AiPredictionEvent.objects.all()
        total = queryset.count()
        completed = queryset.filter(status=AiPredictionEvent.Status.COMPLETED).count()
        rejected = queryset.exclude(status=AiPredictionEvent.Status.COMPLETED).count()
        payload = {
            "total_events": total,
            "completed_events": completed,
            "rejected_events": rejected,
            "model_versions": list(queryset.values_list("model_version", flat=True).distinct()),
        }
        return Response(AiAuditSummarySerializer(payload).data)
