import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Device",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "fcm_token",
                    models.CharField(
                        max_length=512,
                        unique=True,
                        verbose_name="FCM token",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        blank=True, default="", max_length=64, verbose_name="Название"
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="Активно"),
                ),
                (
                    "last_seen_at",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Последний контакт"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Создано"),
                ),
            ],
            options={
                "verbose_name": "Устройство",
                "verbose_name_plural": "Устройства",
                "ordering": ["-last_seen_at"],
            },
        ),
        migrations.CreateModel(
            name="DeviceFileState",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "file_url",
                    models.CharField(max_length=500, verbose_name="URL файла"),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Ожидание"),
                            ("downloading", "Скачивается"),
                            ("done", "Скачано"),
                            ("error", "Ошибка"),
                        ],
                        default="pending",
                        max_length=16,
                        verbose_name="Статус",
                    ),
                ),
                (
                    "progress",
                    models.PositiveSmallIntegerField(
                        default=0, help_text="0..100", verbose_name="Прогресс, %"
                    ),
                ),
                (
                    "file_size",
                    models.BigIntegerField(default=0, verbose_name="Размер, байт"),
                ),
                (
                    "error_message",
                    models.CharField(
                        blank=True,
                        default="",
                        max_length=500,
                        verbose_name="Сообщение об ошибке",
                    ),
                ),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "device",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="file_states",
                        to="device.device",
                        verbose_name="Устройство",
                    ),
                ),
            ],
            options={
                "verbose_name": "Статус файла на устройстве",
                "verbose_name_plural": "Статусы файлов на устройствах",
                "ordering": ["-updated_at"],
            },
        ),
        migrations.AddIndex(
            model_name="devicefilestate",
            index=models.Index(
                fields=["device", "status"], name="device_devi_device__bb09c8_idx"
            ),
        ),
        migrations.AddConstraint(
            model_name="devicefilestate",
            constraint=models.UniqueConstraint(
                fields=("device", "file_url"), name="unique_device_file"
            ),
        ),
    ]
