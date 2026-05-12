from django.urls import path
from .views import (
    SyllabusUploadView, SyllabusDetailView, SyllabusListView,
    GeneratePracticeQuestionsView, PracticeHistoryView,
    SectionCreateView, SectionDeleteView, CourseSectionsView,
)

urlpatterns = [
    # Syllabus
    path('syllabus/upload/', SyllabusUploadView.as_view(), name='syllabus-upload'),
    path('syllabus/<int:course_id>/', SyllabusDetailView.as_view(), name='syllabus-detail'),
    path('syllabus/', SyllabusListView.as_view(), name='syllabus-list'),

    # Sections with video
    path('sections/add/', SectionCreateView.as_view(), name='section-add'),
    path('sections/<int:section_id>/delete/', SectionDeleteView.as_view(), name='section-delete'),
    path('sections/<int:course_id>/', CourseSectionsView.as_view(), name='course-sections'),

    # AI Practice
    path('practice/generate/', GeneratePracticeQuestionsView.as_view(), name='practice-generate'),
    path('practice/history/', PracticeHistoryView.as_view(), name='practice-history'),
]
