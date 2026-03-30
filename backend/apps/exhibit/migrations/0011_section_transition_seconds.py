from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("exhibit", "0010_hall_transition_map_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="section",
            name="transition_seconds",
            field=models.PositiveIntegerField(
                default=0,
                verbose_name="Время перехода к след. разделу (сек)",
            ),
        ),
    ]
