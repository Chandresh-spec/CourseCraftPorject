# study_assistant/urls.py
from django.urls import path
from .views import quiz_by_topic

urlpatterns = [
    path('explaination/', quiz_by_topic, name='india_quiz'),
]


