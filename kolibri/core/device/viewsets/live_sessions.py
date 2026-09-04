import time
from django.core.cache import cache
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

CACHE_KEY = "kolibri_active_live_sessions"
SESSION_TIMEOUT_SECONDS = 7200  # 2 hours


class LiveClassSessionView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        sessions = cache.get(CACHE_KEY) or {}
        now = time.time()
        active_sessions = {
            cid: s
            for cid, s in sessions.items()
            if now - s.get("updated_at", 0) < SESSION_TIMEOUT_SECONDS
            and s.get("active", False)
        }
        return Response(active_sessions)

    def post(self, request):
        class_id = request.data.get("class_id")
        if not class_id:
            return Response(
                {"error": "class_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        active = request.data.get("active", True)
        room_name = request.data.get("room_name", f"kolibri_class_{class_id}")
        teacher_name = getattr(request.user, "full_name", None) or request.user.username

        sessions = cache.get(CACHE_KEY) or {}
        now = time.time()

        if active:
            sessions[class_id] = {
                "active": True,
                "room_name": room_name,
                "class_id": class_id,
                "teacher_name": teacher_name,
                "updated_at": now,
            }
        else:
            sessions.pop(class_id, None)

        cache.set(CACHE_KEY, sessions, timeout=SESSION_TIMEOUT_SECONDS)
        return Response({"status": "ok", "class_id": class_id, "active": active})
