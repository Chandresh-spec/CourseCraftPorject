from rest_framework import serializers
from .models import CourseSyllabus, PracticeSession, SyllabusSection


class SyllabusSectionSerializer(serializers.ModelSerializer):
    video_url = serializers.SerializerMethodField()

    class Meta:
        model = SyllabusSection
        fields = ['id', 'syllabus', 'title', 'description', 'video', 'video_url',
                  'duration_minutes', 'order', 'is_preview', 'created_at']
        read_only_fields = ['created_at']

    def get_video_url(self, obj):
        if obj.video:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.video.url)
            return obj.video.url
        return None



class SyllabusSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.course_name', read_only=True)
    sections = SyllabusSectionSerializer(many=True, read_only=True)

    class Meta:
        model = CourseSyllabus
        fields = [
            'id', 'course', 'course_name', 'content',
            'syllabus_file', 'topics', 'sections', 'created_at', 'updated_at'
        ]
        read_only_fields = ['uploaded_by', 'created_at', 'updated_at']


class SyllabusUploadSerializer(serializers.ModelSerializer):
    """Used when an instructor uploads/updates a syllabus."""
    class Meta:
        model = CourseSyllabus
        fields = ['course', 'content', 'syllabus_file', 'topics']


class PracticeSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PracticeSession
        fields = ['id', 'course', 'topic_asked', 'questions_generated', 'created_at']
        read_only_fields = ['user', 'created_at']
