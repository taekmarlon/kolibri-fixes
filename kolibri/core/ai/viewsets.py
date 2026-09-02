import logging

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from kolibri.core.ai.universal_client import call_ai_chat
from kolibri.core.ai.universal_client import get_ai_config
from kolibri.core.ai.universal_client import PROVIDER_PRESETS
from kolibri.core.device.permissions import IsSuperuser

logger = logging.getLogger(__name__)


class AiStatusView(APIView):
    """
    Returns public status of AI Tutor (whether it is enabled by super admin).
    """

    permission_classes = (AllowAny,)

    def get(self, request):
        config = get_ai_config()
        return Response(
            {
                "enabled": config["enabled"],
                "provider": config["provider"],
                "model_name": config["model_name"],
                "has_api_key": bool(config["api_key"])
                or config["provider"] == "ollama",
                "available_providers": [
                    {"id": k, "name": v["name"], "default_model": v["default_model"]}
                    for k, v in PROVIDER_PRESETS.items()
                ],
            }
        )


class AiChatView(APIView):
    """
    Student & Learner Chat endpoint. Injects resource context and queries universal AI model.
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        config = get_ai_config()
        if not config["enabled"]:
            return Response(
                {"error": "AI Tutor is currently disabled by administrator."},
                status=status.HTTP_403_FORBIDDEN,
            )

        data = request.data
        messages = data.get("messages", [])
        if not messages:
            return Response(
                {"error": "Messages array is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        context_data = data.get("context", {})
        context_info = ""
        if context_data:
            title = context_data.get("title", "")
            description = context_data.get("description", "")
            kind = context_data.get("kind", "")
            question = context_data.get("question", "")
            context_info = (
                f"Topic/Resource: {title}\nType: {kind}\nDescription: {description}"
            )
            if question:
                context_info += f"\nCurrent Problem / Question: {question}"

        grade_level = data.get("grade_level", "elementary")

        try:
            ai_reply = call_ai_chat(
                messages, context_info=context_info, grade_level=grade_level
            )
            return Response({"response": ai_reply, "reply": ai_reply})
        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(f"AI Chat Error: {e}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AiGenerateQuizView(APIView):
    """
    Coach Quiz Generator. Generates structured practice questions.
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        config = get_ai_config()
        if not config["enabled"]:
            return Response(
                {"error": "AI Assistant is currently disabled by administrator."},
                status=status.HTTP_403_FORBIDDEN,
            )

        data = request.data
        topic = data.get("topic", "General Math")
        grade_level = data.get("grade_level", "Middle School")
        num_questions = int(data.get("num_questions", 5))

        prompt = (
            f"Generate {num_questions} high-quality educational quiz questions for grade level '{grade_level}' "
            f"on the topic '{topic}'.\n"
            f"Provide the output formatted as clear numbered questions with multiple choice options (A, B, C, D), "
            f"the correct answer, and a short explanation for each."
        )

        messages = [{"role": "user", "content": prompt}]

        try:
            ai_reply = call_ai_chat(messages)
            return Response({"quiz": ai_reply, "topic": topic})
        except Exception as e:
            logger.error(f"AI Quiz Generation Error: {e}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AiGenerateLessonView(APIView):
    """
    Coach Lesson Plan Generator.
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        config = get_ai_config()
        if not config["enabled"]:
            return Response(
                {"error": "AI Assistant is currently disabled by administrator."},
                status=status.HTTP_403_FORBIDDEN,
            )

        data = request.data
        topic = data.get("topic", "Science")
        grade_level = data.get("grade_level", "Elementary")

        prompt = (
            f"Create a structured lesson plan for grade level '{grade_level}' on topic '{topic}'.\n"
            f"Include:\n"
            f"1. Learning Objectives\n"
            f"2. Key Vocabulary\n"
            f"3. 3-Part Lesson Flow (Warm-up, Core Concept, Guided Practice)\n"
            f"4. Discussion Questions\n"
            f"5. Quick Assessment Rubric"
        )

        messages = [{"role": "user", "content": prompt}]

        try:
            ai_reply = call_ai_chat(messages)
            return Response({"lesson_plan": ai_reply, "lesson": ai_reply, "topic": topic})
        except Exception as e:
            logger.error(f"AI Lesson Generation Error: {e}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AiTestConnectionView(APIView):
    """
    Super Admin Test Connection endpoint. Tests any provider credentials before saving.
    """

    permission_classes = (IsSuperuser,)

    def post(self, request):
        data = request.data
        provider = data.get("provider", "gemini")
        api_key = data.get("api_key", "")
        api_url = data.get("api_url", "")
        model_name = data.get("model_name", "")

        preset = PROVIDER_PRESETS.get(provider, PROVIDER_PRESETS["gemini"])

        test_config = {
            "enabled": True,
            "provider": provider,
            "api_key": api_key,
            "api_url": api_url or preset["default_url"],
            "model_name": model_name or preset["default_model"],
            "system_prompt": "You are a test assistant. Respond with 'Connection Successful!'",
            "is_gemini_native": preset.get("is_gemini_native", False),
        }

        messages = [{"role": "user", "content": "Ping test connection."}]

        try:
            from kolibri.core.ai.universal_client import _call_gemini_native
            from kolibri.core.ai.universal_client import _call_openai_compatible

            if test_config["is_gemini_native"]:
                reply = _call_gemini_native(
                    messages, test_config["system_prompt"], test_config, timeout=15
                )
            else:
                reply = _call_openai_compatible(
                    messages, test_config["system_prompt"], test_config, timeout=15
                )

            return Response(
                {
                    "success": True,
                    "message": f"Connected to {preset['name']} successfully!",
                    "response": reply,
                }
            )
        except Exception as e:
            logger.error(f"AI Test Connection failed: {e}")
            return Response(
                {
                    "success": False,
                    "error": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
