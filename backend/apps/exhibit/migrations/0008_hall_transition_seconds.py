from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("exhibit", "0006_rename_duration_to_seconds"),
        ("exhibit", "0007_hall_map_image_section_map_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="hall",
            name="transition_seconds",
            field=models.PositiveIntegerField(
                default=60,
                help_text="Время на переход между залами",
                verbose_name="Время перехода (секунд)",
            ),
        ),
    ]
