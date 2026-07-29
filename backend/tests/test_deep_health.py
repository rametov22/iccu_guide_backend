from unittest.mock import patch

from django.test import override_settings

from config.deep_health import build_deep_health_report


@override_settings(DEEP_HEALTH_API_KEY="monitoring-secret")
@patch("config.deep_health.build_deep_health_report")
def test_deep_health_rejects_missing_key_without_running_checks(build_report, client):
    response = client.get("/deep-health/")

    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}
    assert response.headers["Cache-Control"] == "no-store"
    build_report.assert_not_called()


@override_settings(DEEP_HEALTH_API_KEY="monitoring-secret")
@patch("config.deep_health.build_deep_health_report")
def test_deep_health_rejects_wrong_key_without_running_checks(build_report, client):
    response = client.get("/deep-health/", headers={"X-API-Key": "wrong-secret"})

    assert response.status_code == 401
    build_report.assert_not_called()


@override_settings(DEEP_HEALTH_API_KEY="monitoring-secret")
@patch("config.deep_health.build_deep_health_report")
def test_deep_health_returns_report_with_http_200_even_when_service_is_down(build_report, client):
    build_report.return_value = {
        "status": "down",
        "generated_at": "2026-07-29T10:00:00Z",
        "services": [
            {
                "service": "redis",
                "status": "down",
                "detail": "PING or read/write failed",
            }
        ],
    }

    response = client.get("/deep-health/", headers={"X-API-Key": "monitoring-secret"})

    assert response.status_code == 200
    assert response.json() == build_report.return_value
    assert response.headers["Cache-Control"] == "no-store"


@override_settings(DEEP_HEALTH_API_KEY="")
@patch("config.deep_health.build_deep_health_report")
def test_deep_health_is_disabled_when_server_key_is_empty(build_report, client):
    response = client.get("/deep-health/", headers={"X-API-Key": "any-key"})

    assert response.status_code == 401
    build_report.assert_not_called()


def test_deep_health_allows_only_get(client):
    response = client.post("/deep-health/")

    assert response.status_code == 405


@override_settings(DEEP_HEALTH_DEADLINE_SECONDS=1.5)
def test_deep_health_report_uses_the_worst_service_status():
    checks = (
        ("backend", lambda: {"service": "backend", "status": "ok", "detail": "passed"}),
        ("backend-asgi", lambda: {"service": "backend-asgi", "status": "degraded", "detail": "slow"}),
        ("db", lambda: {"service": "db", "status": "down", "detail": "failed"}),
        ("redis", lambda: {"service": "redis", "status": "ok", "detail": "passed"}),
    )

    with patch("config.deep_health.CHECKS", checks):
        report = build_deep_health_report()

    assert report["status"] == "down"
    assert report["generated_at"].endswith("Z")
    assert [item["service"] for item in report["services"]] == [
        "backend",
        "backend-asgi",
        "db",
        "redis",
    ]
