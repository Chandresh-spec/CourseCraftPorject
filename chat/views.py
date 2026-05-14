# study_assistant/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from huggingface_hub import InferenceClient
import os


HF_API_KEY = os.environ.get("HF_API_KEY", "")
client = InferenceClient(api_key=HF_API_KEY)

@api_view(['POST'])
def quiz_by_topic(request):
    
    try:
        topic = request.data.get("topic")
        if not topic:
            return Response(
                {"error": "Please provide a 'topic' in the request body."},
                status=status.HTTP_400_BAD_REQUEST
            )

        completion = client.chat.completions.create(
            model="Qwen/Qwen2.5-72B-Instruct",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful study assistant. Provide clear, concise, and educational answers to the student's questions."
                },
                {
                    "role": "user",
                    "content": f"{topic}"
                }
            ],
        )
        message_content = completion.choices[0].message['content']

        return Response({"info": message_content}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )









