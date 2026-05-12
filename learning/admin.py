from django.contrib import admin
from .models import CourseSyllabus, PracticeSession, SyllabusSection


class SyllabusSectionInline(admin.TabularInline):
    model = SyllabusSection
    extra = 1
    fields = ['order', 'title', 'description', 'video', 'duration_minutes', 'is_preview']


@admin.register(CourseSyllabus)
class CourseSyllabusAdmin(admin.ModelAdmin):
    list_display = ['course', 'uploaded_by', 'created_at', 'updated_at']
    search_fields = ['course__course_name', 'uploaded_by__username']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [SyllabusSectionInline]


@admin.register(SyllabusSection)
class SyllabusSectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'syllabus', 'order', 'duration_minutes', 'is_preview']
    list_filter = ['is_preview', 'syllabus__course']
    search_fields = ['title']


@admin.register(PracticeSession)
class PracticeSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'topic_asked', 'created_at']
    list_filter = ['created_at', 'course']
    search_fields = ['user__username', 'topic_asked']
    readonly_fields = ['created_at']
