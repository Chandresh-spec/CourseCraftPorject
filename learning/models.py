from django.db import models
from django.contrib.auth import get_user_model
from courses.models import Courses

User = get_user_model()


class CourseSyllabus(models.Model):
    """
    Stores the syllabus uploaded by a course instructor.
    Linked 1-to-1 with a Course.
    """
    course = models.OneToOneField(
        Courses,
        on_delete=models.CASCADE,
        related_name='syllabus'
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='uploaded_syllabi'
    )
    # Raw text content extracted from the uploaded file / typed manually
    content = models.TextField(
        help_text="Full syllabus text extracted from the uploaded file."
    )
    # Optional PDF upload
    syllabus_file = models.FileField(
        upload_to='syllabi/',
        null=True,
        blank=True
    )
    topics = models.TextField(
        blank=True,
        help_text="Comma-separated list of key topics (auto-generated or manual)."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Course Syllabus"
        verbose_name_plural = "Course Syllabi"

    def __str__(self):
        return f"Syllabus – {self.course.course_name}"


class SyllabusSection(models.Model):
    """
    One module/section inside a syllabus.
    Instructors add title, description and an optional video per section.
    """
    syllabus = models.ForeignKey(
        CourseSyllabus,
        on_delete=models.CASCADE,
        related_name='sections'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    video = models.FileField(
        upload_to='section_videos/',
        null=True,
        blank=True,
        help_text="Upload an MP4 / WebM lecture video."
    )
    duration_minutes = models.PositiveIntegerField(
        default=0,
        help_text="Approximate duration in minutes."
    )
    order = models.PositiveIntegerField(default=0, help_text="Display order (0 = first).")
    is_preview = models.BooleanField(default=False, help_text="Free preview for non-enrolled users.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Syllabus Section"
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"[{self.order}] {self.title} — {self.syllabus.course.course_name}"


class PracticeSession(models.Model):
    """
    Records a practice Q&A session a student had for a course.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='practice_sessions')
    course = models.ForeignKey(Courses, on_delete=models.CASCADE, related_name='practice_sessions')
    topic_asked = models.CharField(max_length=300)
    questions_generated = models.TextField(
        help_text="AI-generated questions stored as JSON text."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} – {self.course.course_name} – {self.created_at.date()}"
