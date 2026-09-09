import json
import logging
import os
import shutil

import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "kolibri.deployment.default.settings.base"
)
try:
    django.setup()
except Exception as e:
    logging.warning("Django setup warning: %s", e)

from kolibri.core.auth.models import Facility
from kolibri.core.device.models import DeviceSettings

logger = logging.getLogger("sync_render_init")
logger.setLevel(logging.INFO)

logger.info("==> [Render Init] Running sync_render_init.py...")

# 1. Configure DeviceSettings for AI Tutor
try:
    ds = DeviceSettings.objects.first()
    if ds:
        extra = ds.extra_settings or {}
        extra["ai_tutor_enabled"] = True
        extra["ai_provider"] = os.environ.get("KOLIBRI_AI_PROVIDER", "gemini")
        gemini_key = os.environ.get("GEMINI_API_KEY") or extra.get("ai_api_key", "")
        if gemini_key:
            extra["ai_api_key"] = gemini_key
        extra["ai_model_name"] = os.environ.get(
            "KOLIBRI_AI_MODEL", "gemini-3.5-flash-lite"
        )
        ds.extra_settings = extra
        ds.save()
        logger.info("==> [Render Init] DeviceSettings AI Tutor successfully enabled.")
except Exception as e:
    logger.warning("==> [Render Init] Error updating DeviceSettings: %s", e)

# 2. Sync Cedarhall Facility Theme
try:
    theme_file = os.path.join(os.path.dirname(__file__), "cedarhall_theme.json")
    if os.path.exists(theme_file):
        with open(theme_file, "r", encoding="utf-8") as f:
            theme_data = json.load(f)

        theme_data["background_image_url"] = (
            "/static/assets/default_theme/facility_wallpaper.jpg"
        )

        facilities = list(Facility.objects.all())
        for facility in facilities:
            if "cedarhall" in facility.name.lower() or len(facilities) == 1:
                dataset = facility.dataset
                ef = dataset.extra_fields or {}
                ef["theme"] = theme_data
                ef["facility_code"] = "cha"
                dataset.extra_fields = ef
                dataset.save()
                logger.info(
                    "==> [Render Init] Applied Cedarhall theme to facility: %s",
                    facility.name,
                )
except Exception as e:
    logger.warning("==> [Render Init] Error updating Facility theme: %s", e)

# 3. Ensure background wallpaper exists in media directory too
try:
    media_bg_dir = os.path.expanduser("~/.kolibri/media/facility_themes/backgrounds")
    os.makedirs(media_bg_dir, exist_ok=True)
    src_wp = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "kolibri",
        "plugins",
        "default_theme",
        "static",
        "assets",
        "default_theme",
        "facility_wallpaper.jpg",
    )
    dst_wp = os.path.join(
        media_bg_dir,
        "4bb2008815e146189c8b593c97fd4e2d_ae69a3a5b85efeb298f23b01c423f68f.jpg",
    )
    if os.path.exists(src_wp) and not os.path.exists(dst_wp):
        shutil.copyfile(src_wp, dst_wp)
        logger.info("==> [Render Init] Wallpaper copied to media folder.")
except Exception as e:
    logger.warning("==> [Render Init] Error copying wallpaper: %s", e)

logger.info("==> [Render Init] Complete.")
