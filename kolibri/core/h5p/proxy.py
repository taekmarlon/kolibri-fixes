import json
import logging
import os

import requests
from csp.decorators import csp_exempt
from django.conf import settings
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)

H5P_NODE_BASE_URL = getattr(
    settings,
    "H5P_NODE_BASE_URL",
    os.environ.get("KOLIBRI_H5P_NODE_URL", "http://127.0.0.1:8080"),
)

HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
    "content-length",
    "host",
}

INJECTED_CLIENT_BRIDGE = """
<style>
/* Kolibri H5P Integration Styling */
body {
    margin: 0 !important;
    padding: 12px 16px !important;
    background-color: #f8fafc !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
}
.h5p-create {
    background: transparent !important;
}
#h5p-content-form {
    max-width: 100% !important;
    margin: 0 auto !important;
    background: #ffffff !important;
    padding: 16px 20px !important;
    border-radius: 8px !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
}
.h5p-editor-iframe {
    min-height: 680px !important;
    width: 100% !important;
    display: block !important;
}
.h5p-editor, .h5peditor {
    min-height: 680px !important;
}
#save-h5p {
    display: none !important;
}
.alert-warning {
    display: none !important;
}
</style>
<script>
(function() {
    function notifyParent(msgObj) {
        if (window.parent && window.parent !== window) {
            window.parent.postMessage(msgObj, '*');
        }
    }

    function checkHubReady() {
        var editorIframe = document.querySelector('.h5p-editor-iframe');
        if (editorIframe && editorIframe.contentDocument) {
            var doc = editorIframe.contentDocument;
            var isReady = doc.querySelector('.h5p-hub-content-type-list, .h5p-hub-client-drop-down, .h5p-hub, .h5peditor-form');
            if (isReady) {
                notifyParent({ type: 'KOLIBRI_H5P_READY' });
                try {
                    if (editorIframe.contentWindow) {
                        editorIframe.contentWindow.dispatchEvent(new Event('resize'));
                    }
                } catch (e) {}
                return;
            }
        }
        setTimeout(checkHubReady, 250);
    }

    function setupFormProtection() {
        // Document-level capture phase listener guarantees no native form POST escapes
        document.addEventListener('submit', function(e) {
            if (e.target && e.target.id === 'h5p-content-form') {
                var hasValidLibrary = false;
                var libraryInput = document.querySelector('input[name="library"]');
                if (libraryInput && libraryInput.value) {
                    hasValidLibrary = true;
                }
                var editorIframe = document.querySelector('.h5p-editor-iframe');
                if (editorIframe && editorIframe.contentDocument) {
                    if (editorIframe.contentDocument.querySelector('.h5peditor-form')) {
                        hasValidLibrary = true;
                    }
                }

                if (!hasValidLibrary) {
                    e.preventDefault();
                    e.stopImmediatePropagation();
                    notifyParent({
                        type: 'KOLIBRI_H5P_VALIDATION_ERROR',
                        message: 'Please select an interactive activity type and fill in the required fields before saving.'
                    });
                    return false;
                }
            }
        }, true);

        // Document-level bubble phase listener prevents native HTML form submission
        // All H5P saving is performed asynchronously via $.ajax
        document.addEventListener('submit', function(e) {
            if (e.target && e.target.id === 'h5p-content-form') {
                e.preventDefault();
            }
        }, false);
    }

    function setupBridge() {
        setupFormProtection();
        checkHubReady();

        if (window.H5P && window.H5P.jQuery) {
            window.H5P.jQuery(document).ajaxComplete(function(event, xhr, settings) {
                try {
                    if (settings.type === 'POST' && (settings.url.indexOf('/new') !== -1 || settings.url.indexOf('/edit/') !== -1 || settings.url === '')) {
                        var data = (typeof xhr.responseJSON === 'object' && xhr.responseJSON !== null) ? xhr.responseJSON : JSON.parse(xhr.responseText);
                        if (data && data.contentId) {
                            var title = '';
                            try {
                                if (settings.data) {
                                    var reqData = typeof settings.data === 'string' ? JSON.parse(settings.data) : settings.data;
                                    if (reqData && reqData.params && reqData.params.metadata && reqData.params.metadata.title) {
                                        title = reqData.params.metadata.title;
                                    }
                                }
                            } catch (pe) {}

                            if (!title) {
                                var titleInput = document.querySelector('input[name="title"]') || document.getElementById('title');
                                if (titleInput && titleInput.value) {
                                    title = titleInput.value;
                                }
                            }

                            notifyParent({
                                type: 'KOLIBRI_H5P_SAVED',
                                contentId: data.contentId,
                                title: title
                            });
                        }
                    }
                } catch (e) {}
            });
        } else {
            setTimeout(setupBridge, 100);
        }
    }

    if (document.readyState === 'complete' || document.readyState === 'interactive') {
        setupBridge();
    } else {
        document.addEventListener('DOMContentLoaded', setupBridge);
    }
})();
</script>
"""


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(xframe_options_exempt, name="dispatch")
@method_decorator(csp_exempt, name="dispatch")
class H5PProxyView(View):
    """
    Reverse proxy view that forwards /h5p/* requests to the local Node.js H5P authoring and playback engine.
    Ensures seamless same-origin communication and strips external branding.
    """

    def _get_forward_headers(self, request):
        headers = {}
        for key, value in request.META.items():
            if key.startswith("HTTP_"):
                header_name = key[5:].replace("_", "-")
                # Do not forward hop-by-hop or cache validation headers to upstream Node.js
                # This guarantees upstream returns HTTP 200 with full content and prevents 304 cache reuse
                if header_name.lower() in HOP_BY_HOP_HEADERS or header_name.lower() in (
                    "if-none-match",
                    "if-modified-since",
                ):
                    continue
                headers[header_name] = value
            elif key in ("CONTENT_TYPE", "CONTENT_LENGTH"):
                header_name = key.replace("_", "-")
                if header_name.lower() not in HOP_BY_HOP_HEADERS:
                    headers[header_name] = value

        user = getattr(request, "user", None)
        if user and getattr(user, "is_authenticated", False):
            headers["X-Kolibri-User-Id"] = str(user.id)
            user_full_name = getattr(user, "full_name", "") or getattr(
                user, "username", "Kolibri User"
            )
            headers["X-Kolibri-User-Name"] = user_full_name
            headers["X-Kolibri-User-Email"] = getattr(user, "email", "") or ""

        return headers

    def _inject_html_bridge(self, html_text):
        try:
            parent_bridge = (
                "<script>\n"
                "if (window.parent && window.parent !== window) {\n"
                "    try {\n"
                "        Object.defineProperty(window.parent, 'H5PEditor', {\n"
                "            get: function() { return window.H5PEditor; },\n"
                "            set: function(v) { window.H5PEditor = v; },\n"
                "            configurable: true\n"
                "        });\n"
                "        Object.defineProperty(window.parent, 'H5PIntegration', {\n"
                "            get: function() { return window.H5PIntegration; },\n"
                "            set: function(v) { window.H5PIntegration = v; },\n"
                "            configurable: true\n"
                "        });\n"
                "    } catch(e) {}\n"
                "}\n"
                "</script>\n"
            )

            if "<head>" in html_text:
                html_text = html_text.replace("<head>", f"<head>\n{parent_bridge}", 1)
            elif "<script>" in html_text:
                html_text = f"{parent_bridge}{html_text}"

            target_integration_check = (
                "window.H5PIntegration = parent.H5PIntegration ||"
            )
            replacement_integration_check = (
                "window.H5PIntegration = (window.parent === window && "
                "window.parent.H5PIntegration) ||"
            )
            if target_integration_check in html_text:
                html_text = html_text.replace(
                    target_integration_check, replacement_integration_check, 1
                )

            last_body_idx = html_text.rfind("</body>")
            if last_body_idx != -1:
                html_text = (
                    html_text[:last_body_idx]
                    + INJECTED_CLIENT_BRIDGE
                    + html_text[last_body_idx:]
                )
            else:
                html_text = f"{html_text}{INJECTED_CLIENT_BRIDGE}"
            return html_text.encode("utf-8")
        except Exception as err:
            logger.error(f"Error injecting H5P client bridge: {err}")
            return html_text.encode("utf-8")

    def _create_django_response(self, request, resp):
        content_type = resp.headers.get("content-type", "")
        body = resp.content

        is_json_response = "application/json" in content_type
        trimmed_text = resp.text.strip()
        if not is_json_response and (
            trimmed_text.startswith(("{", "[")) and trimmed_text.endswith(("}", "]"))
        ):
            try:
                json.loads(trimmed_text)
                is_json_response = True
                content_type = "application/json"
            except (ValueError, TypeError):
                pass

        is_html_document = (
            not is_json_response
            and request.method in ("GET", "HEAD")
            and "text/html" in content_type
            and ("<html" in resp.text.lower() or "<body" in resp.text.lower())
        )

        if is_html_document:
            body = self._inject_html_bridge(resp.text)

        django_response = HttpResponse(
            body,
            status=resp.status_code,
            content_type=content_type,
        )

        for key, value in resp.headers.items():
            if key.lower() not in HOP_BY_HOP_HEADERS and key.lower() not in (
                "content-type",
                "content-encoding",
                "x-frame-options",
                "content-security-policy",
                "content-security-policy-report-only",
                "etag",
                "last-modified",
            ):
                django_response[key] = value

        django_response.xframe_options_exempt = True
        django_response._csp_exempt = True
        django_response["X-Frame-Options"] = "SAMEORIGIN"

        if "text/html" in content_type:
            django_response["Cache-Control"] = (
                "no-cache, no-store, must-revalidate, max-age=0"
            )
            django_response["Pragma"] = "no-cache"
            django_response["Expires"] = "0"

        return django_response

    def dispatch(self, request, path="", *args, **kwargs):
        clean_path = path.lstrip("/")
        if not clean_path:
            return HttpResponseRedirect("/h5p/new")

        # Guard against native HTML form POST submissions which lack the required JSON payload
        if request.method == "POST" and clean_path.rstrip("/") == "new":
            content_type = request.META.get("CONTENT_TYPE", "")
            if (
                "multipart/form-data" in content_type
                or "x-www-form-urlencoded" in content_type
            ):
                logger.info(
                    "Prevented malformed native form POST to /h5p/new; redirecting to /h5p/new"
                )
                return HttpResponseRedirect("/h5p/new")

        target_url = f"{H5P_NODE_BASE_URL}/h5p/{clean_path}"
        query_string = request.META.get("QUERY_STRING")
        if query_string:
            target_url = f"{target_url}?{query_string}"

        forward_headers = self._get_forward_headers(request)
        data = request.body if request.method in ("POST", "PUT", "PATCH") else None

        try:
            resp = requests.request(
                method=request.method,
                url=target_url,
                headers=forward_headers,
                data=data,
                allow_redirects=False,
                timeout=60,
            )
        except requests.exceptions.RequestException as err:
            logger.warning(f"H5P engine request failed for {target_url}: {err}")
            return HttpResponse(
                "<h3>H5P Interactive Engine is temporarily unavailable.</h3>"
                "<p>Please ensure the local H5P server is running.</p>",
                status=503,
                content_type="text/html",
            )

        return self._create_django_response(request, resp)
