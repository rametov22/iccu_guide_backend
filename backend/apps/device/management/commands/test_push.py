"""
Утилита для тестирования FCM-уведомлений.

Использование:

  # Проверить, что Firebase подключился
  python manage.py test_push --check

  # Отправить тестовый push на конкретный токен
  python manage.py test_push --token <FCM_TOKEN>

  # Отправить всем активным устройствам в БД
  python manage.py test_push --all

  # С кастомным заголовком/телом
  python manage.py test_push --token <TOKEN> --title "Hello" --body "World"
"""

from django.core.management.base import BaseCommand

from device.models import Device
from device.services import is_configured, send_push_to_all, send_push_to_tokens


class Command(BaseCommand):
    help = "Отправить тестовый push через Firebase Cloud Messaging"

    def add_arguments(self, parser):
        parser.add_argument("--token", type=str, help="FCM-токен получателя")
        parser.add_argument("--all", action="store_true", help="Отправить всем активным устройствам")
        parser.add_argument("--check", action="store_true", help="Только проверить, что Firebase сконфигурирован")
        parser.add_argument("--title", default="Тест", help="Заголовок уведомления")
        parser.add_argument("--body", default="Это тестовый push", help="Текст уведомления")

    def handle(self, *args, **opts):
        self.stdout.write(self.style.MIGRATE_HEADING("=== Firebase status ==="))
        self.stdout.write(f"Configured: {is_configured()}")
        self.stdout.write(f"Active devices in DB: {Device.objects.filter(is_active=True).count()}")

        if opts["check"]:
            return

        if not is_configured():
            self.stderr.write(self.style.ERROR(
                "Firebase не настроен. Проверьте FIREBASE_CREDENTIALS_PATH в .env "
                "и что файл доступен внутри контейнера."
            ))
            return

        title = opts["title"]
        body = opts["body"]
        data = {"action": "test"}

        if opts["all"]:
            self.stdout.write(self.style.MIGRATE_HEADING("\n=== Sending to all active devices ==="))
            result = send_push_to_all(title=title, body=body, data=data)
        elif opts["token"]:
            self.stdout.write(self.style.MIGRATE_HEADING("\n=== Sending to single token ==="))
            result = send_push_to_tokens([opts["token"]], title=title, body=body, data=data)
        else:
            self.stderr.write(self.style.ERROR(
                "Нужен один из флагов: --token <TOKEN>, --all или --check"
            ))
            return

        if result is None:
            self.stderr.write(self.style.ERROR("Push не отправлен (см. логи backend)"))
            return

        self.stdout.write(self.style.SUCCESS(f"\nResult: {result}"))
        if result["failure_count"] == 0 and result["success_count"] > 0:
            self.stdout.write(self.style.SUCCESS("✓ Push доставлен в Firebase"))
        elif result["invalid_tokens"]:
            self.stderr.write(self.style.WARNING(
                f"Битых токенов: {len(result['invalid_tokens'])} (устройства деактивированы)"
            ))
