from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("exhibit", "0008_hall_transition_seconds"),
    ]

    operations = [
        migrations.AddField(
            model_name="section",
            name="video",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to="sections/videos/",
                verbose_name="Видео раздела",
            ),
        ),
    ]
