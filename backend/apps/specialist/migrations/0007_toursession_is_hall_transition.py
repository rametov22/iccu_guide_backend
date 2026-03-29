from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("specialist", "0006_toursession_break_remaining_seconds_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="toursession",
            name="is_hall_transition",
            field=models.BooleanField(
                default=False,
                verbose_name="Переход между залами",
            ),
        ),
    ]
