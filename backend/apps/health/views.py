from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    """Minimal service-liveness endpoint for the Phase 3 backend foundation."""

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response(
            {
                "status": "ok",
                "service": "MediCare API",
            }
        )
