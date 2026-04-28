from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("device", "0001_initial"),
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
