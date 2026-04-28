"""
Firebase Cloud Messaging — клиент.

Конфигурация (берётся из .env):
  FIREBASE_CREDENTIALS_PATH — путь к service-account JSON
  (или пустая строка, тогда push'ы тихо логируются и не отправляются)

Установка зависимости:  pip install firebase-admin
"""

import logging

from decouple import config

__all__ = ("send_push_to_all", "send_push_to_tokens", "is_configured")

log = logging.getLogger(__name__)

FIREBASE_CREDENTIALS_PATH = config("FIREBASE_CREDENTIALS_PATH", default="")

_app = None
_initialized = False


def _ensure_app():
    """Lazy-init: инициализируем firebase_admin при первом обращении."""
    global _app, _initialized
    if _initialized:
        return _app

    _initialized = True
    if not FIREBASE_CREDENTIALS_PATH:
        log.warning("Firebase не настроен (FIREBASE_CREDENTIALS_PATH пуст)")
        return None

    try:
        import firebase_admin
        from firebase_admin import credentials

        cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
        _app = firebase_admin.initialize_app(cred)
        return _app
    except Exception as e:
        log.exception("Не удалось инициализировать Firebase: %s", e)
        return None


def is_configured():
    return bool(FIREBASE_CREDENTIALS_PATH)


def _coerce_data(data):
    """FCM требует, чтобы все значения в data были строками."""
    return {str(k): str(v) for k, v in (data or {}).items()}


def send_push_to_tokens(tokens, title, body, data=None):
    """
    Шлёт push на список FCM-токенов через MulticastMessage.

    Возвращает dict со счётчиками success_count / failure_count и списком
    «битых» токенов (которые надо деактивировать в Device).
    """
    tokens = [t for t in (tokens or []) if t]
    if not tokens:
        return {"success_count": 0, "failure_count": 0, "invalid_tokens": []}

    if _ensure_app() is None:
        return {"success_count": 0, "failure_count": 0, "invalid_tokens": []}

    from firebase_admin import messaging

    msg = messaging.MulticastMessage(
        tokens=list(tokens),
        notification=messaging.Notification(title=title, body=body),
        data=_coerce_data(data),
    )
    try:
        resp = messaging.send_each_for_multicast(msg)
    except Exception as e:
        log.exception("FCM send_each_for_multicast failed: %s", e)
        return {"success_count": 0, "failure_count": len(tokens), "invalid_tokens": []}

    invalid = []
    for token, r in zip(tokens, resp.responses):
        if r.success:
            continue
        err = r.exception
        # NotRegistered / InvalidRegistration / SenderIdMismatch — токен мёртв
        code = getattr(err, "code", "")
        if code in ("registration-token-not-registered", "invalid-argument"):
            invalid.append(token)

    return {
        "success_count": resp.success_count,
        "failure_count": resp.failure_count,
        "invalid_tokens": invalid,
    }


def send_push_to_all(title, body, data=None):
    """
    Шлёт push всем активным устройствам.

    Берёт токены из БД (Device.is_active=True), шлёт батчами по 500
    (лимит FCM на multicast).
    """
    from ..models import Device

    if not is_configured():
        log.warning("Firebase не настроен — push не отправлен")
        return None

    qs = Device.objects.filter(is_active=True).values_list("fcm_token", flat=True)
    tokens = list(qs)
    if not tokens:
        return {"success_count": 0, "failure_count": 0, "invalid_tokens": []}

    aggregate = {"success_count": 0, "failure_count": 0, "invalid_tokens": []}
    for i in range(0, len(tokens), 500):
        chunk = tokens[i:i + 500]
        r = send_push_to_tokens(chunk, title, body, data)
        aggregate["success_count"] += r["success_count"]
        aggregate["failure_count"] += r["failure_count"]
        aggregate["invalid_tokens"].extend(r["invalid_tokens"])

    # Деактивируем устройства с битыми токенами
    if aggregate["invalid_tokens"]:
        Device.objects.filter(fcm_token__in=aggregate["invalid_tokens"]).update(is_active=False)
        log.info("Деактивировано %d устройств с битыми FCM-токенами", len(aggregate["invalid_tokens"]))

    return aggregate
