import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("device", "0001_initial"),
        ("tour", "0006_alter_touristsession_device_token_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="touristsession",
            name="device",
            field=models.ForeignKey(
                blank=True,
                help_text="Постоянный iPad (по FCM-токену)",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="tourist_sessions",
                to="device.device",
                verbose_name="Устройство",
            ),
        ),
    ]
