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


def _get_variants(val):
    val_str = str(val).strip()
    if not val_str:
        return []
    res = [val_str]
    clean = "".join(ch for ch in val_str if ch.isalnum()).lower()
    if clean:
        res.append(clean)
    for prefix in (
        "phiedu_class_",
        "kolibri_class_",
        "phiedu_room_",
        "phiedu_",
        "room_",
    ):
        if val_str.startswith(prefix):
            sub = val_str[len(prefix) :]
            res.append(sub)
            res.append("".join(ch for ch in sub if ch.isalnum()).lower())
    return [r for r in res if r]


def _get_session_keys(class_id, room_name):
    return set(_get_variants(class_id) + _get_variants(room_name))


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
        room_name = str(request.data.get("room_name", "")).strip()

        if not class_id and not room_name:
            return Response(
                {"error": "Either class_id or room_name is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        room_name = room_name or f"phiedu_class_{class_id}"
        class_id = class_id or room_name
        active = request.data.get("active", True)
        teacher_name = getattr(request.user, "full_name", None) or getattr(
            request.user, "username", "Participant"
        )

        sessions = _read_sessions()
        now = time.time()
        keys = _get_session_keys(class_id, room_name)

        if active:
            session_data = {
                "active": True,
                "room_name": room_name,
                "class_id": class_id,
                "teacher_name": teacher_name,
                "updated_at": now,
            }
            for k in keys:
                sessions[k] = session_data
        else:
            for k in keys:
                sessions.pop(k, None)

        # prune expired sessions
        sessions = {
            cid: s
            for cid, s in sessions.items()
            if now - s.get("updated_at", 0) < SESSION_TIMEOUT_SECONDS
        }

        _write_sessions(sessions)
        return Response(
            {
                "status": "ok",
                "class_id": class_id,
                "room_name": room_name,
                "active": active,
            }
        )
