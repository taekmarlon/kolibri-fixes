import json
import os
import time

from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from kolibri.utils.conf import KOLIBRI_HOME

SESSION_TIMEOUT_SECONDS = 7200  # 2 hours
SESSIONS_FILE = os.path.join(KOLIBRI_HOME, "active_live_sessions.json")


def _read_sessions():
    if not os.path.exists(SESSIONS_FILE):
        return {}
    try:
        with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _write_sessions(data):
    try:
        tmp_file = f"{SESSIONS_FILE}.tmp"
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(data, f)
        os.replace(tmp_file, SESSIONS_FILE)
    except Exception:
        pass


class LiveClassSessionView(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request):
        sessions = _read_sessions()
        now = time.time()
        active_sessions = {
            str(cid): s
            for cid, s in sessions.items()
            if now - s.get("updated_at", 0) < SESSION_TIMEOUT_SECONDS
            and s.get("active", False)
        }
        return Response(active_sessions)

    def post(self, request):
        class_id = str(request.data.get("class_id", "")).strip()
        if not class_id:
            return Response(
                {"error": "class_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        active = request.data.get("active", True)
        room_name = request.data.get("room_name", f"kolibri_class_{class_id}")
        teacher_name = getattr(request.user, "full_name", None) or getattr(
            request.user, "username", "Teacher"
        )

        sessions = _read_sessions()
        now = time.time()
        normalized_id = "".join(ch for ch in class_id if ch.isalnum()).lower()

        if active:
            session_data = {
                "active": True,
                "room_name": room_name,
                "class_id": class_id,
                "teacher_name": teacher_name,
                "updated_at": now,
            }
            sessions[class_id] = session_data
            if normalized_id:
                sessions[normalized_id] = session_data
        else:
            sessions.pop(class_id, None)
            if normalized_id:
                sessions.pop(normalized_id, None)

        # prune expired sessions
        sessions = {
            cid: s
            for cid, s in sessions.items()
            if now - s.get("updated_at", 0) < SESSION_TIMEOUT_SECONDS
        }

        _write_sessions(sessions)
        return Response({"status": "ok", "class_id": class_id, "active": active})
