from django.urls import path

from . import views

app_name = "chatbot"

urlpatterns = [path("api/ask-ai/", views.AskAiView.as_view(), name="ask_ai")]
