import json
import logging
import os
import urllib.error
import urllib.request

logger = logging.getLogger(__name__)

# Default provider presets
PROVIDER_PRESETS = {
    "gemini": {
        "name": "Google Gemini",
        "default_url": "https://generativelanguage.googleapis.com/v1beta/models",
        "default_model": "gemini-1.5-flash",
        "env_var": "GEMINI_API_KEY",
        "is_gemini_native": True,
    },
    "openai": {
        "name": "OpenAI",
        "default_url": "https://api.openai.com/v1/chat/completions",
        "default_model": "gpt-4o-mini",
        "env_var": "OPENAI_API_KEY",
        "is_gemini_native": False,
    },
    "deepseek": {
        "name": "DeepSeek",
        "default_url": "https://api.deepseek.com/v1/chat/completions",
        "default_model": "deepseek-chat",
        "env_var": "DEEPSEEK_API_KEY",
        "is_gemini_native": False,
    },
    "groq": {
        "name": "Groq (Llama 3.3 / 3.1)",
        "default_url": "https://api.groq.com/openai/v1/chat/completions",
        "default_model": "llama-3.3-70b-versatile",
        "env_var": "GROQ_API_KEY",
        "is_gemini_native": False,
    },
    "huggingface": {
        "name": "Hugging Face",
        "default_url": "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-7B-Instruct/v1/chat/completions",
        "default_model": "Qwen/Qwen2.5-7B-Instruct",
        "env_var": "HUGGINGFACE_API_KEY",
        "is_gemini_native": False,
    },
    "ollama": {
        "name": "Local Ollama (Offline)",
        "default_url": "http://localhost:11434/v1/chat/completions",
        "default_model": "llama3.2",
        "env_var": "OLLAMA_API_KEY",
        "is_gemini_native": False,
    },
    "custom": {
        "name": "Custom OpenAI-Compatible Endpoint",
        "default_url": "",
        "default_model": "",
        "env_var": "AI_API_KEY",
        "is_gemini_native": False,
    },
}

DEFAULT_SYSTEM_PROMPT = (
    "You are a friendly, encouraging, and knowledgeable AI Tutor in the Kolibri Learning Platform.\n"
    "Your goal is to explain concepts clearly in your own original words using simple everyday analogies,\n"
    "step-by-step reasoning, and clear formatting.\n"
    "Format math formulas and scientific notation using standard LaTeX with $ for inline math (e.g. $x^2 + y^2 = r^2$) "
    "and $$ for block math equations.\n\n"
    "INTERACTIVE HTML5 ACTIVITIES & SIMULATIONS:\n"
    "Whenever explaining a concept, teaching a tutorial, or providing practice, "
    "include an engaging, fully self-contained, responsive interactive HTML5/CSS/JavaScript widget inside an "
    "```html ... ``` code block.\n"
    "The widget MUST be interactive using keyboard and mouse (such as clickable buttons, drag-and-drop, sliders, "
    "interactive canvas graphics, keyboard navigation, score trackers, instant feedback, and reset buttons).\n"
    "All CSS styling and JavaScript logic must be inline within <style> and <script> tags with zero external dependencies "
    "so that it works 100% offline.\n"
    "Keep explanations structured, friendly, clear, and easy to understand."
)


def get_ai_config():
    """
    Retrieves current AI Tutor configuration from DeviceSettings or environment variables.
    """
    from kolibri.core.device.utils import get_device_setting

    extra_settings = get_device_setting("extra_settings") or {}

    provider = extra_settings.get("ai_provider", "gemini") or "gemini"
    preset = PROVIDER_PRESETS.get(provider, PROVIDER_PRESETS["gemini"])

    enabled = bool(extra_settings.get("ai_tutor_enabled", False))

    # Check key: database override first, then environment variable
    api_key = extra_settings.get("ai_api_key", "")
    if not api_key and preset.get("env_var"):
        api_key = os.environ.get(preset["env_var"], "") or os.environ.get(
            "GEMINI_API_KEY", ""
        )

    api_url = extra_settings.get("ai_api_url", "") or preset["default_url"]
    model_name = extra_settings.get("ai_model_name", "") or preset["default_model"]
    system_prompt = extra_settings.get("ai_system_prompt", "") or DEFAULT_SYSTEM_PROMPT

    return {
        "enabled": enabled,
        "provider": provider,
        "api_key": api_key,
        "api_url": api_url,
        "model_name": model_name,
        "system_prompt": system_prompt,
        "is_gemini_native": preset.get("is_gemini_native", False),
    }


GRADE_LEVEL_PROMPTS = {
    "pre_elementary": (
        "You are a cheerful, magical learning companion for young kids (ages 4-7 / Kindergarten & Pre-Elem).\n"
        "Tone: Enthusiastic, warm, playful, and full of wonder.\n"
        "Style Guidelines:\n"
        "- Use short, simple sentences (1-2 lines max).\n"
        "- Use lots of fun emojis (🍎 🐱 🐶 🌟 🎈 🎨) and visual emoji pictures.\n"
        "- Use cute analogies with animals, toys, colors, and bedtime stories.\n"
        "- Include simple, colorful interactive HTML5 click/tap games (e.g., clicking stars or animals to count them, matching shapes) in ```html```.\n"
        "- Always praise the child's effort with virtual stars and high fives (⭐⭐⭐ High five!)."
    ),
    "elementary": (
        "You are an energetic, fun AI study coach for elementary students (Grades 1-5).\n"
        "Tone: Friendly, encouraging, adventurous like a cool video game guide.\n"
        "Style Guidelines:\n"
        "- Explain concepts step-by-step using fun numbered cards (Step 1, Step 2, Step 3).\n"
        "- Use relatable real-world analogies (e.g. pizza slices for fractions, LEGO blocks for volume, skateboard for inertia).\n"
        "- Include fun emojis (🚀 💡 🎮 🍕 🎯 🏆).\n"
        "- Include an interactive HTML5 simulation, minigame, or practice tool with mouse and keyboard engagement in ```html```.\n"
        "- Include a '💡 Quick Check' or '⭐ Fun Trivia' at the end to keep them engaged."
    ),
    "secondary": (
        "You are an inspiring, top-tier academic tutor and STEM mentor for secondary & high school students (Grades 6-12).\n"
        "Tone: Intelligent, supportive, clear, and structured.\n"
        "Style Guidelines:\n"
        "- Provide deep conceptual understanding with step-by-step mathematical derivations and logical proofs.\n"
        "- Format formulas cleanly using LaTeX ($...$ and $$...$$).\n"
        "- Connect concepts to real-world engineering, science, economics, and history.\n"
        "- Include interactive HTML5 STEM simulations, parameter sliders, physics/math canvas graphs, or interactive problem solvers in ```html```.\n"
        "- Highlight Key Takeaways 📌 and Exam Pro-Tips 💡."
    ),
}


def call_ai_chat(
    messages,
    system_instruction=None,
    context_info=None,
    grade_level="elementary",
    timeout=30,
):
    """
    Unified router that sends chat messages to the configured provider with grade-adaptive prompting.
    messages: list of {"role": "user"|"assistant"|"system", "content": "..."}
    """
    config = get_ai_config()

    if not config["enabled"]:
        raise PermissionError("AI Tutor is currently disabled by administrator.")

    api_key = config["api_key"]
    if not api_key and config["provider"] != "ollama":
        raise ValueError(
            f"API Key for {config['provider'].upper()} is not configured. Please set it in Device Settings or environment variable."
        )

    grade_guidance = GRADE_LEVEL_PROMPTS.get(
        grade_level, GRADE_LEVEL_PROMPTS["elementary"]
    )
    sys_prompt = system_instruction or config["system_prompt"]
    sys_prompt = f"{sys_prompt}\n\nGRADE LEVEL ADAPTATION:\n{grade_guidance}"

    if context_info:
        sys_prompt += f"\n\nCURRENT RESOURCE / LESSON CONTEXT:\n{context_info}"

    if config["is_gemini_native"]:
        return _call_gemini_native(messages, sys_prompt, config, timeout=timeout)
    else:
        return _call_openai_compatible(messages, sys_prompt, config, timeout=timeout)


def _call_gemini_native(messages, system_prompt, config, timeout=30):  # noqa: C901
    """
    Calls Google Gemini REST API v1beta with automatic retries and fallback.
    """
    import time

    model = config["model_name"] or "gemini-1.5-flash"
    api_key = config["api_key"]
    base_url = config["api_url"].rstrip("/")

    url = f"{base_url}/{model}:generateContent?key={api_key}"

    # Format history into Gemini contents format
    gemini_contents = []
    for msg in messages:
        role = "user" if msg["role"] == "user" else "model"
        gemini_contents.append(
            {"role": role, "parts": [{"text": msg.get("content", "")}]}
        )

    payload = {
        "contents": gemini_contents,
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "generationConfig": {
            "temperature": 0.8,
            "maxOutputTokens": 2048,
        },
    }

    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=req_data, headers={"Content-Type": "application/json"}
    )

    last_error = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                res_body = response.read().decode("utf-8")
                data = json.loads(res_body)
                candidates = data.get("candidates", [])
                if candidates:
                    candidate = candidates[0]
                    parts = candidate.get("content", {}).get("parts", [])
                    text_parts = [p.get("text", "") for p in parts if p.get("text")]
                    if text_parts:
                        return "".join(text_parts)
                    if candidate.get("finishReason") == "RECITATION":
                        logger.warning(
                            "Gemini recitation filter triggered, re-prompting..."
                        )
                        # Modify payload to emphasize original paraphrase
                        payload["systemInstruction"] = {
                            "parts": [
                                {
                                    "text": (
                                        f"{system_prompt}\n\nPlease summarize and explain everything in your own original words with intuitive examples."
                                    )
                                }
                            ]
                        }
                        req = urllib.request.Request(
                            url,
                            data=json.dumps(payload).encode("utf-8"),
                            headers={"Content-Type": "application/json"},
                        )
                        continue
                return "No response received from AI model."
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8", errors="ignore")
            logger.error(f"Gemini API Error ({e.code}): {err_msg}")
            try:
                err_json = json.loads(err_msg)
                message = err_json.get("error", {}).get("message", err_msg)
            except Exception:
                message = err_msg
            raise RuntimeError(f"Google Gemini Error: {message}")
        except urllib.error.URLError as e:
            last_error = e
            logger.warning(f"Gemini connection attempt {attempt + 1} failed: {e}")
            time.sleep(1 * (attempt + 1))
        except Exception as e:
            last_error = e
            break

    if isinstance(last_error, urllib.error.URLError):
        raise RuntimeError(
            f"Unable to reach Google Gemini ({last_error.reason}). Please check your internet connection and try again."
        )
    raise RuntimeError(f"Failed to connect to AI provider: {str(last_error)}")


def _call_openai_compatible(messages, system_prompt, config, timeout=30):  # noqa: C901
    """
    Calls any OpenAI-compatible Chat Completions API (DeepSeek, Groq, OpenAI, Ollama, Hugging Face).
    """
    import time

    url = config["api_url"]
    if not url:
        raise ValueError("API Endpoint URL is missing.")

    api_key = config["api_key"]
    model = config["model_name"]

    # Build formatted messages with system prompt at top
    openai_messages = [{"role": "system", "content": system_prompt}]
    for msg in messages:
        if msg["role"] != "system":
            openai_messages.append(
                {
                    "role": "assistant" if msg["role"] == "model" else msg["role"],
                    "content": msg.get("content", ""),
                }
            )

    payload = {
        "model": model,
        "messages": openai_messages,
        "temperature": 0.7,
        "max_tokens": 2048,
    }

    headers = {
        "Content-Type": "application/json",
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=req_data, headers=headers)

    last_error = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                res_body = response.read().decode("utf-8")
                data = json.loads(res_body)
                choices = data.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content", "")
                return "No response received from AI model."
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8", errors="ignore")
            logger.error(f"OpenAI-Compatible API Error ({e.code}): {err_msg}")
            try:
                err_json = json.loads(err_msg)
                message = err_json.get("error", {}).get("message", err_msg)
            except Exception:
                message = err_msg
            raise RuntimeError(f"AI Provider Error: {message}")
        except urllib.error.URLError as e:
            last_error = e
            logger.warning(f"AI connection attempt {attempt + 1} failed: {e}")
            time.sleep(1 * (attempt + 1))
        except Exception as e:
            last_error = e
            break

    if isinstance(last_error, urllib.error.URLError):
        raise RuntimeError(
            f"Unable to reach AI provider at {url} ({last_error.reason}). Please verify connection and try again."
        )
    raise RuntimeError(f"Failed to connect to AI provider: {str(last_error)}")
