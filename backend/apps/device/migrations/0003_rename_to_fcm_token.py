from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("device", "0002_rename_device_devi_device__bb09c8_idx_device_devi_device__5b8e27_idx"),
    ]

    operations = [
        migrations.RenameField(
            model_name="device",
            old_name="onesignal_player_id",
            new_name="fcm_token",
        ),
        migrations.AlterField(
            model_name="device",
            name="fcm_token",
            field=models.CharField(
                max_length=512,
                unique=True,
                verbose_name="FCM token",
            ),
        ),
    ]
