import hmac
import json
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from datetime import UTC, datetime
from urllib.request import urlopen
from uuid import uuid4

from django.conf import settings
from django.db import connections
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from redis import Redis
from redis.backoff import NoBackoff
from redis.retry import Retry

STATUS_PRIORITY = {"ok": 0, "degraded": 1, "down": 2}


def _service_result(service, status, detail, started_at):
    return {
        "service": service,
        "status": status,
        "detail": detail,
        "latency_ms": round((time.perf_counter() - started_at) * 1000, 2),
    }


def _check_backend():
    started_at = time.perf_counter()
    return _service_result("backend", "ok", "application is responsive", started_at)


def _check_backend_asgi():
    service = "backend-asgi"
    started_at = time.perf_counter()
    try:
        with urlopen(
            settings.DEEP_HEALTH_ASGI_URL,
            timeout=settings.DEEP_HEALTH_CLIENT_TIMEOUT_SECONDS,
        ) as response:
            payload = json.load(response)
            if response.status != 200 or payload.get("status") != "ok":
                raise ValueError("unexpected healthcheck response")
    except Exception:
        return _service_result(service, "down", "healthcheck failed", started_at)
    return _service_result(service, "ok", "healthcheck passed", started_at)


def _check_database():
    service = "db"
    started_at = time.perf_counter()
    connection = connections["default"]
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            if cursor.fetchone() != (1,):
                raise ValueError("unexpected database response")
    except Exception:
        return _service_result(service, "down", "query failed", started_at)
    finally:
        connection.close()
    return _service_result(service, "ok", "query passed", started_at)


def _check_redis():
    service = "redis"
    started_at = time.perf_counter()
    key = f"deep-health:{uuid4().hex}"
    client = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=1,
        socket_connect_timeout=settings.DEEP_HEALTH_CLIENT_TIMEOUT_SECONDS,
        socket_timeout=settings.DEEP_HEALTH_CLIENT_TIMEOUT_SECONDS,
        retry=Retry(NoBackoff(), 0),
    )
    try:
        if not client.ping():
            raise ValueError("PING failed")
        client.set(key, "ok", ex=5)
        if client.get(key) != b"ok":
            raise ValueError("read/write failed")
    except Exception:
        return _service_result(service, "down", "PING or read/write failed", started_at)
    finally:
        client.close()
    return _service_result(service, "ok", "PING and read/write passed", started_at)


CHECKS = (
    ("backend", _check_backend),
    ("backend-asgi", _check_backend_asgi),
    ("db", _check_database),
    ("redis", _check_redis),
)


def _collect_services():
    deadline = time.monotonic() + settings.DEEP_HEALTH_DEADLINE_SECONDS
    executor = ThreadPoolExecutor(max_workers=len(CHECKS), thread_name_prefix="deep-health")
    futures = [(service, executor.submit(check)) for service, check in CHECKS]
    services = []

    for service, future in futures:
        remaining = max(0, deadline - time.monotonic())
        try:
            services.append(future.result(timeout=remaining))
        except TimeoutError:
            services.append(
                {
                    "service": service,
                    "status": "down",
                    "detail": "shared deadline exceeded",
                }
            )
        except Exception:
            services.append(
                {
                    "service": service,
                    "status": "down",
                    "detail": "healthcheck failed",
                }
            )

    executor.shutdown(wait=False, cancel_futures=True)
    return services


def build_deep_health_report():
    services = _collect_services()
    status = max(services, key=lambda item: STATUS_PRIORITY[item["status"]])["status"]
    return {
        "status": status,
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "services": services,
    }


@require_GET
def deep_health(request):
    expected_key = settings.DEEP_HEALTH_API_KEY
    supplied_key = request.headers.get("X-API-Key", "")
    if not expected_key or not supplied_key or not hmac.compare_digest(supplied_key, expected_key):
        response = JsonResponse({"detail": "Unauthorized"}, status=401)
        response["Cache-Control"] = "no-store"
        return response

    response = JsonResponse(build_deep_health_report(), status=200)
    response["Cache-Control"] = "no-store"
    return response
