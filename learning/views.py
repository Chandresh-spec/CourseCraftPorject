from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from huggingface_hub import InferenceClient
import json
import os

from .models import CourseSyllabus, PracticeSession, SyllabusSection
from .serializers import SyllabusSerializer, SyllabusUploadSerializer, PracticeSessionSerializer, SyllabusSectionSerializer
from courses.models import Courses

# Reuse the same HF client from chat app
HF_API_KEY = os.environ.get("HF_API_KEY", "")
client = InferenceClient(api_key=HF_API_KEY)


# ─── Instructor: Upload / Update Syllabus ─────────────────────────────────────

class SyllabusUploadView(APIView):
    """
    POST /learning/syllabus/upload/
    Instructors upload a syllabus (text + optional PDF) for one of their courses.
    If a syllabus already exists for that course it is replaced.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        course_id = request.data.get('course')
        if not course_id:
            return Response({"error": "course id is required."}, status=status.HTTP_400_BAD_REQUEST)

        course = get_object_or_404(Courses, pk=course_id)

        # Upsert: update if exists, else create
        syllabus, created = CourseSyllabus.objects.update_or_create(
            course=course,
            defaults={
                'uploaded_by': request.user,
                'content': request.data.get('content', ''),
                'topics': request.data.get('topics', ''),
                'syllabus_file': request.FILES.get('syllabus_file', None),
            }
        )

        serializer = SyllabusSerializer(syllabus)
        return Response(
            {
                "message": "Syllabus uploaded successfully!" if created else "Syllabus updated successfully!",
                "syllabus": serializer.data
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )


# ─── Get Syllabus for a Course ────────────────────────────────────────────────

class SyllabusDetailView(APIView):
    """
    GET /learning/syllabus/<course_id>/
    Returns the syllabus for a given course (public – enrolled students need it).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        course = get_object_or_404(Courses, pk=course_id)
        try:
            syllabus = course.syllabus
        except CourseSyllabus.DoesNotExist:
            return Response(
                {"error": "No syllabus found for this course."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = SyllabusSerializer(syllabus)
        return Response(serializer.data)


# ─── List all syllabi (for students browsing) ─────────────────────────────────

class SyllabusListView(APIView):
    """
    GET /learning/syllabus/
    Returns all uploaded syllabi (summary only).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        syllabi = CourseSyllabus.objects.select_related('course').all()
        serializer = SyllabusSerializer(syllabi, many=True)
        return Response(serializer.data)


# ─── AI Practice Question Generator ──────────────────────────────────────────

class GeneratePracticeQuestionsView(APIView):
    """
    POST /learning/practice/generate/
    Body: { "course_id": 1, "topic": "Linked Lists", "num_questions": 5 }

    Uses the course syllabus as context + the requested topic to generate
    MCQ practice questions via the Hugging Face Inference API.
    Saves the session for history.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        course_id = request.data.get('course_id')
        topic = request.data.get('topic', '').strip()
        num_q = int(request.data.get('num_questions', 5))

        if not course_id or not topic:
            return Response(
                {"error": "Both 'course_id' and 'topic' are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        course = get_object_or_404(Courses, pk=course_id)

        # Get syllabus context (if available)
        syllabus_context = ""
        try:
            syllabus_context = course.syllabus.content[:3000]  # limit tokens
        except CourseSyllabus.DoesNotExist:
            syllabus_context = f"Course: {course.course_name}. Level: {course.levels}."

        prompt = f"""You are an expert educator. Based on the following course syllabus, generate exactly {num_q} high-quality multiple-choice practice questions about the topic: "{topic}".

SYLLABUS CONTEXT:
{syllabus_context}

REQUIREMENTS:
- Generate exactly {num_q} MCQ questions
- Each question must have 4 options labeled A, B, C, D
- Clearly mark the correct answer
- Add a brief explanation for the correct answer
- Return ONLY valid JSON in this exact format:

{{
  "topic": "{topic}",
  "questions": [
    {{
      "id": 1,
      "question": "Question text here?",
      "options": {{
        "A": "Option A text",
        "B": "Option B text",
        "C": "Option C text",
        "D": "Option D text"
      }},
      "correct_answer": "A",
      "explanation": "Brief explanation why A is correct."
    }}
  ]
}}

Return ONLY the JSON. No extra text."""

        try:
            completion = client.chat.completions.create(
                model="zai-org/GLM-4.7-Flash:novita",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=3000,
            )
            raw_content = completion.choices[0].message['content']

            # Extract JSON from the response
            json_start = raw_content.find('{')
            json_end = raw_content.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = raw_content[json_start:json_end]
                questions_data = json.loads(json_str)
            else:
                questions_data = {"topic": topic, "raw": raw_content}

            # Save session
            PracticeSession.objects.create(
                user=request.user,
                course=course,
                topic_asked=topic,
                questions_generated=json.dumps(questions_data)
            )

            return Response(questions_data, status=status.HTTP_200_OK)

        except json.JSONDecodeError:
            # Return raw if JSON parsing fails
            return Response({"topic": topic, "raw": raw_content}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ─── Practice History ─────────────────────────────────────────────────────────

class PracticeHistoryView(APIView):
    """
    GET /learning/practice/history/?course_id=<id>
    Returns the logged-in user's practice sessions for a course.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        course_id = request.query_params.get('course_id')
        qs = PracticeSession.objects.filter(user=request.user)
        if course_id:
            qs = qs.filter(course_id=course_id)
        qs = qs.order_by('-created_at')[:20]
        serializer = PracticeSessionSerializer(qs, many=True)
        return Response(serializer.data)


# ─── Section: Create a section with optional video ───────────────────────────

class SectionCreateView(APIView):
    """
    POST /learning/sections/add/
    Instructor adds a section (title, description, video, order) to a syllabus.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        syllabus_id = request.data.get('syllabus')
        if not syllabus_id:
            return Response({"error": "syllabus id is required."}, status=status.HTTP_400_BAD_REQUEST)

        syllabus = get_object_or_404(CourseSyllabus, pk=syllabus_id)

        section = SyllabusSection(
            syllabus=syllabus,
            title=request.data.get('title', ''),
            description=request.data.get('description', ''),
            order=int(request.data.get('order', 0)),
            duration_minutes=int(request.data.get('duration_minutes', 0)),
            is_preview=request.data.get('is_preview', 'false').lower() == 'true',
        )
        if 'video' in request.FILES:
            section.video = request.FILES['video']
        section.save()

        serializer = SyllabusSectionSerializer(section, context={'request': request})
        return Response({"message": "Section added!", "section": serializer.data}, status=status.HTTP_201_CREATED)


class SectionDeleteView(APIView):
    """
    DELETE /learning/sections/<section_id>/delete/
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, section_id):
        section = get_object_or_404(SyllabusSection, pk=section_id)
        section.delete()
        return Response({"message": "Section deleted."}, status=status.HTTP_204_NO_CONTENT)


# ─── Get all sections for a course ───────────────────────────────────────────

class CourseSectionsView(APIView):
    """
    GET /learning/sections/<course_id>/
    Returns ordered sections with video URLs for a course.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        course = get_object_or_404(Courses, pk=course_id)
        try:
            syllabus = course.syllabus
        except CourseSyllabus.DoesNotExist:
            return Response({"error": "No syllabus found for this course."}, status=status.HTTP_404_NOT_FOUND)

        sections = syllabus.sections.all().order_by('order', 'created_at')
        serializer = SyllabusSectionSerializer(sections, many=True, context={'request': request})
        return Response({"course": course.course_name, "sections": serializer.data})
