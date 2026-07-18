from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

import pytest


def test_healthcheck(client):
    response = client.get("/healthcheck/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.django_db
def test_custom_superuser():
    user = get_user_model().objects.create_superuser(
        username="admin",
        password="strong-test-password",
    )
    assert user.is_staff is True
    assert user.is_superuser is True
    assert user.role == user.Role.ADMIN


def test_media_storage():
    name = default_storage.save("verification/example.txt", ContentFile(b"ipad-tour"))
    assert default_storage.exists(name)
    assert default_storage.size(name) == 9
