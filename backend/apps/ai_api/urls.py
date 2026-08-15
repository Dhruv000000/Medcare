from django.urls import path

from .views import HeartRiskPredictionView, SymptomChatView


urlpatterns = [
    path("heart-risk/predict/", HeartRiskPredictionView.as_view(), name="ai-heart-risk-predict"),
    path("symptom-chat/", SymptomChatView.as_view(), name="ai-symptom-chat"),
]
