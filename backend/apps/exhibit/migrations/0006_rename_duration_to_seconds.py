from django.db import migrations, models


def convert_minutes_to_seconds(apps, schema_editor):
    Section = apps.get_model("exhibit", "Section")
    for sec in Section.objects.all():
        sec.duration_minutes = sec.duration_minutes * 60
        sec.break_duration_minutes = sec.break_duration_minutes * 60
        sec.save(update_fields=["duration_minutes", "break_duration_minutes"])


def convert_seconds_to_minutes(apps, schema_editor):
    Section = apps.get_model("exhibit", "Section")
    for sec in Section.objects.all():
        sec.duration_seconds = max(1, sec.duration_seconds // 60)
        sec.break_duration_seconds = sec.break_duration_seconds // 60
        sec.save(update_fields=["duration_seconds", "break_duration_seconds"])


class Migration(migrations.Migration):

    dependencies = [
        ("exhibit", "0005_section_break_duration_minutes"),
    ]

    operations = [
        # 1. Convert existing data from minutes to seconds (while fields still have old names)
        migrations.RunPython(convert_minutes_to_seconds, convert_seconds_to_minutes),
        # 2. Rename fields
        migrations.RenameField(
            model_name="section",
            old_name="duration_minutes",
            new_name="duration_seconds",
        ),
        migrations.RenameField(
            model_name="section",
            old_name="break_duration_minutes",
            new_name="break_duration_seconds",
        ),
        # 3. Update defaults and verbose names
        migrations.AlterField(
            model_name="section",
            name="duration_seconds",
            field=models.PositiveIntegerField(
                default=600,
                verbose_name="Длительность (секунд)",
            ),
        ),
        migrations.AlterField(
            model_name="section",
            name="break_duration_seconds",
            field=models.PositiveIntegerField(
                default=300,
                help_text="Длительность перерыва после завершения этого раздела",
                verbose_name="Перерыв после раздела (секунд)",
            ),
        ),
    ]
