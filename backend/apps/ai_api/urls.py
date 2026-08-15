from django.urls import path

from .views import HeartRiskPredictionView


urlpatterns = [
    path("heart-risk/predict/", HeartRiskPredictionView.as_view(), name="ai-heart-risk-predict"),
]
