"""Replace current_location with current_section in TourSession."""

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("exhibit", "0002_hall_section_migrate_data"),
        ("specialist", "0003_toursession_current_location_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="toursession",
            name="current_location",
        ),
        migrations.AddField(
            model_name="toursession",
            name="current_section",
            field=models.ForeignKey(
                blank=True,
                help_text="Раздел, который специалист сейчас показывает",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="active_sessions",
                to="exhibit.section",
                verbose_name="Текущий раздел",
            ),
        ),
    ]
