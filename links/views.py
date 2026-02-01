import json
import logging
from typing import Any, Dict, Optional

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import urlparse

from .models import Link, LinkClick

logger = logging.getLogger(__name__)

def links(request):
    return render(request=request, template_name="links.html")

def _is_valid_origin(request) -> bool:
    origin = request.META.get("HTTP_ORIGIN") or request.META.get("HTTP_REFERER")
    if not origin:
        return False

    try:
        parsed = urlparse(origin)
        origin_host = parsed.netloc
    except Exception:
        return False

    return origin_host == request.get_host()


def _parse_json_body(request) -> Optional[Dict[str, Any]]:
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        logger.exception("Invalid JSON body in tracking request")
        return None


def _get_client_ip(request) -> Optional[str]:
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _persist_click(payload: Dict[str, Any], request) -> None:
    try:
        link_obj = None
        link_id = payload.get("link_id") if isinstance(payload, dict) else None
        
        if link_id:
            link_obj = Link.objects.filter(pk=link_id).first()

        referrer = payload.get("referrer") or request.META.get("HTTP_REFERER")
        user_agent = request.META.get("HTTP_USER_AGENT") or payload.get("user_agent")
        client_x = payload.get("client_x")
        client_y = payload.get("client_y")
        viewport = payload.get("viewport") or {}
        viewport_width = viewport.get("width")
        viewport_height = viewport.get("height")
        ip_address = _get_client_ip(request)

        LinkClick.objects.create(
            link=link_obj,
            payload=payload,
            referrer=referrer,
            user_agent=user_agent,
            client_x=client_x,
            client_y=client_y,
            viewport_width=viewport_width,
            viewport_height=viewport_height,
            ip_address=ip_address,
        )
    except Exception:
        logger.exception("Failed to persist tracking event")


@csrf_exempt
def track_click(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid method")

    if not _is_valid_origin(request):
        logger.warning(
            "Rejected tracking request due invalid origin: %s",
            request.META.get("HTTP_ORIGIN") or request.META.get("HTTP_REFERER"),
        )
        return HttpResponseBadRequest("Invalid origin")

    content_type = request.META.get("CONTENT_TYPE", "") or ""
    if "application/json" not in content_type:
        logger.warning("Rejected tracking request due invalid content-type: %s", content_type)
        return HttpResponseBadRequest("Invalid content type")

    payload = _parse_json_body(request)
    if payload is None:
        return HttpResponseBadRequest("Invalid payload")

    _persist_click(payload, request)

    return HttpResponse(status=204)
