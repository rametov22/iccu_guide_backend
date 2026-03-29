from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("exhibit", "0009_section_video"),
    ]

    operations = [
        migrations.AddField(
            model_name="hall",
            name="transition_map_image",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="halls/transition_maps/",
                verbose_name="Карта перехода к залу",
                help_text="Показывается туристам при переходе в этот зал",
            ),
        ),
    ]
