from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("exhibit", "0005_section_break_duration_minutes"),
    ]

    operations = [
        migrations.AddField(
            model_name="hall",
            name="map_image",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="halls/maps/",
                verbose_name="Карта зала",
            ),
        ),
        migrations.AddField(
            model_name="section",
            name="map_image",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="sections/maps/",
                verbose_name="Карта раздела",
            ),
        ),
    ]
