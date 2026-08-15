"""Tests for the Phase 11 AI foundation; no prediction accuracy is tested."""

from __future__ import annotations

import unittest
from uuid import UUID

from ai.core_errors import (
    InvalidAIInputError,
    MissingClinicalInformationError,
    ModelUnavailableError,
    UnauthorizedAIRequestError,
    UnsupportedAIRequestError,
    UnsafeAIOutputError,
)
from ai.explainability.contracts import validate_response as validate_explainability_response
from ai.models.contracts import AIRequest, AIResponse, AuthorizationContext, DeferredModel
from ai.preprocessing.contracts import InputSchema, Preprocessor
from ai.services.contracts import AIService, deferred_service
from ai.safety.contracts import SAFE_DISCLAIMER, validate_output, validate_request


class PreprocessingContractTests(unittest.TestCase):
    def setUp(self):
        self.preprocessor = Preprocessor(InputSchema(required_fields={"record_type"}))

    def test_valid_input_is_copied_without_arbitrary_transformation(self):
        source = {"record_type": "consultation"}
        result = self.preprocessor.transform(source, task="future_task")
        self.assertEqual(result.task, "future_task")
        self.assertEqual(result.features, source)
        self.assertIsNot(result.features, source)

    def test_missing_required_input_is_rejected(self):
        with self.assertRaises(MissingClinicalInformationError):
            self.preprocessor.transform({}, task="future_task")

    def test_unknown_input_is_rejected(self):
        with self.assertRaises(InvalidAIInputError):
            self.preprocessor.transform({"record_type": "consultation", "patient_name": "not allowed"}, task="future_task")

    def test_non_mapping_input_is_rejected(self):
        with self.assertRaises(InvalidAIInputError):
            self.preprocessor.transform([], task="future_task")


class AuthorizationContractTests(unittest.TestCase):
    def test_patient_can_access_only_own_patient_scope(self):
        context = AuthorizationContext(user_id=10, role="patient", patient_id=101)
        self.assertTrue(context.can_access_patient(101))
        with self.assertRaises(UnauthorizedAIRequestError):
            context.validate_patient_scope(202)

    def test_doctor_can_access_only_server_derived_authorized_scope(self):
        context = AuthorizationContext(user_id=20, role="doctor", authorized_patient_ids=frozenset({101}))
        self.assertTrue(context.can_access_patient(101))
        with self.assertRaises(UnauthorizedAIRequestError):
            context.validate_patient_scope(202)

    def test_invalid_role_is_rejected(self):
        request = AIRequest(
            task="future_task",
            patient_id=101,
            inputs={},
            authorization=AuthorizationContext(user_id=1, role="unknown", patient_id=101),
        )
        with self.assertRaises(UnauthorizedAIRequestError):
            validate_request(request)


class ModelAndResponseContractTests(unittest.TestCase):
    def test_deferred_model_never_returns_fake_prediction(self):
        with self.assertRaises(ModelUnavailableError):
            DeferredModel().predict({"record_type": "consultation"})

    def test_unsupported_response_has_no_fabricated_result_or_confidence(self):
        response = AIResponse(request_id=UUID(int=0), task="future_task")
        self.assertEqual(response.status, "unsupported")
        self.assertIsNone(response.result)
        self.assertIsNone(response.confidence)
        self.assertEqual(response.as_dict()["disclaimer"], SAFE_DISCLAIMER)

    def test_supported_response_requires_result(self):
        response = AIResponse(request_id=UUID(int=0), task="future_task", status="supported")
        with self.assertRaises(UnsafeAIOutputError):
            validate_explainability_response(response)

    def test_unsafe_claim_is_rejected(self):
        response = AIResponse(request_id=UUID(int=0), task="future_task", result="You have a diagnosis", status="abstained")
        with self.assertRaises(UnsafeAIOutputError):
            validate_output(response)


class ServiceBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.request = AIRequest(
            task="future_task",
            patient_id=101,
            inputs={"record_type": "consultation"},
            authorization=AuthorizationContext(user_id=10, role="patient", patient_id=101),
        )

    def test_default_service_rejects_unsupported_task(self):
        with self.assertRaises(UnsupportedAIRequestError):
            deferred_service().handle(self.request)

    def test_service_rejects_missing_preprocessor_even_if_task_is_enabled(self):
        service = AIService(supported_tasks={"future_task"})
        with self.assertRaises(UnsupportedAIRequestError):
            service.handle(self.request)

    def test_service_rejects_cross_patient_request_before_model(self):
        request = AIRequest(
            task="future_task",
            patient_id=202,
            inputs={"record_type": "consultation"},
            authorization=self.request.authorization,
        )
        service = AIService(supported_tasks={"future_task"})
        with self.assertRaises(UnauthorizedAIRequestError):
            service.handle(request)


if __name__ == "__main__":
    unittest.main()


class AuditMetadataTests(unittest.TestCase):
    def test_audit_metadata_contains_operational_fields_only(self):
        from ai.safety.audit import AIAuditMetadata

        metadata = AIAuditMetadata(
            request_id=UUID(int=0),
            user_id=10,
            role="patient",
            request_type="future_task",
            metadata={"source": "api"},
        ).as_dict()
        self.assertEqual(metadata["user_id"], 10)
        self.assertEqual(metadata["metadata"], {"source": "api"})
        self.assertNotIn("password", metadata)
        self.assertNotIn("patient_notes", metadata)
        self.assertNotIn("raw_input", metadata)
