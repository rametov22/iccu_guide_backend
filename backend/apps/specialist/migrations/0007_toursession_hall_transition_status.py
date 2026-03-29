from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("specialist", "0006_toursession_break_remaining_seconds_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="toursession",
            name="status",
            field=models.CharField(
                choices=[
                    ("waiting", "Ожидание подключений"),
                    ("in_progress", "Тур идёт"),
                    ("on_break", "Перерыв"),
                    ("hall_transition", "Переход между залами"),
                    ("finished", "Завершён"),
                ],
                default="waiting",
                max_length=20,
                verbose_name="Статус",
            ),
        ),
    ]
