import logging

import requests
from decouple import config

__all__ = ("send_push_to_all", "send_push_to_player_ids")

log = logging.getLogger(__name__)

ONESIGNAL_APP_ID = config("ONESIGNAL_APP_ID", default="")
ONESIGNAL_REST_API_KEY = config("ONESIGNAL_REST_API_KEY", default="")
ONESIGNAL_API_URL = "https://onesignal.com/api/v1/notifications"
TIMEOUT = 5


def _post(payload):
    if not ONESIGNAL_APP_ID or not ONESIGNAL_REST_API_KEY:
        log.warning("OneSignal не настроен (ONESIGNAL_APP_ID / REST_API_KEY)")
        return None

    headers = {
        "Authorization": f"Basic {ONESIGNAL_REST_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {"app_id": ONESIGNAL_APP_ID, **payload}
    try:
        r = requests.post(ONESIGNAL_API_URL, json=payload, headers=headers, timeout=TIMEOUT)
        if r.status_code >= 400:
            log.error("OneSignal %s: %s", r.status_code, r.text)
        return r.json() if r.content else None
    except requests.RequestException as e:
        log.exception("OneSignal request failed: %s", e)
        return None


def send_push_to_all(title, body, data=None):
    """Шлёт push всем подписчикам приложения."""
    return _post({
        "included_segments": ["All"],
        "headings": {"en": title, "ru": title},
        "contents": {"en": body, "ru": body},
        "data": data or {},
    })


def send_push_to_player_ids(player_ids, title, body, data=None):
    """Шлёт push на конкретные устройства по player_id."""
    player_ids = [p for p in player_ids if p]
    if not player_ids:
        return None
    return _post({
        "include_player_ids": list(player_ids),
        "headings": {"en": title, "ru": title},
        "contents": {"en": body, "ru": body},
        "data": data or {},
    })
