"""
Replace Location with Hall + Section hierarchy.

Migration steps:
1. Create Hall and Section tables
2. Add nullable section FK to Exhibit
3. Migrate data: Location(level=0) → Hall, Location(level=1) → Section
4. Link existing Exhibits to their new Sections
5. Make section FK non-nullable
6. Remove old location FK from Exhibit
7. Delete Location table
"""

from django.db import migrations, models
import django.db.models.deletion


def migrate_location_to_hall_section(apps, schema_editor):
    """Convert Location tree into Hall + Section flat models."""
    Location = apps.get_model("exhibit", "Location")
    Hall = apps.get_model("exhibit", "Hall")
    Section = apps.get_model("exhibit", "Section")
    Exhibit = apps.get_model("exhibit", "Exhibit")

    # Map old location IDs to new hall/section objects
    location_to_hall = {}
    location_to_section = {}

    # Level 0 (root) locations → Halls
    for loc in Location.objects.filter(parent__isnull=True).order_by("order"):
        hall = Hall.objects.create(
            name=loc.name,
            name_ru=getattr(loc, "name_ru", "") or "",
            name_en=getattr(loc, "name_en", "") or "",
            name_uz=getattr(loc, "name_uz", "") or "",
            description=loc.description,
            description_ru=getattr(loc, "description_ru", "") or "",
            description_en=getattr(loc, "description_en", "") or "",
            description_uz=getattr(loc, "description_uz", "") or "",
            order=loc.order,
            is_active=loc.is_active,
        )
        location_to_hall[loc.pk] = hall

        # Level 1 (child) locations → Sections
        for child in Location.objects.filter(parent=loc).order_by("order"):
            section = Section.objects.create(
                hall=hall,
                name=child.name,
                name_ru=getattr(child, "name_ru", "") or "",
                name_en=getattr(child, "name_en", "") or "",
                name_uz=getattr(child, "name_uz", "") or "",
                description=child.description,
                description_ru=getattr(child, "description_ru", "") or "",
                description_en=getattr(child, "description_en", "") or "",
                description_uz=getattr(child, "description_uz", "") or "",
                order=child.order,
                is_active=child.is_active,
            )
            location_to_section[child.pk] = section

    # Update exhibits to point to sections
    for exhibit in Exhibit.objects.all():
        if exhibit.location_id in location_to_section:
            exhibit.section_id = location_to_section[exhibit.location_id].pk
            exhibit.save(update_fields=["section_id"])


class Migration(migrations.Migration):

    dependencies = [
        ("exhibit", "0001_initial"),
        ("specialist", "0003_toursession_current_location_and_more"),
    ]

    operations = [
        # 1. Create Hall table
        migrations.CreateModel(
            name="Hall",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, verbose_name="Название")),
                ("name_ru", models.CharField(max_length=255, null=True, verbose_name="Название")),
                ("name_en", models.CharField(max_length=255, null=True, verbose_name="Название")),
                ("name_uz", models.CharField(max_length=255, null=True, verbose_name="Название")),
                ("description", models.TextField(blank=True, default="", verbose_name="Описание")),
                ("description_ru", models.TextField(blank=True, default="", null=True, verbose_name="Описание")),
                ("description_en", models.TextField(blank=True, default="", null=True, verbose_name="Описание")),
                ("description_uz", models.TextField(blank=True, default="", null=True, verbose_name="Описание")),
                ("order", models.PositiveIntegerField(default=0, verbose_name="Порядок")),
                ("is_active", models.BooleanField(default=True, verbose_name="Активен")),
            ],
            options={
                "verbose_name": "Зал",
                "verbose_name_plural": "Залы",
                "ordering": ["order", "name"],
            },
        ),
        # 2. Create Section table
        migrations.CreateModel(
            name="Section",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, verbose_name="Название")),
                ("name_ru", models.CharField(max_length=255, null=True, verbose_name="Название")),
                ("name_en", models.CharField(max_length=255, null=True, verbose_name="Название")),
                ("name_uz", models.CharField(max_length=255, null=True, verbose_name="Название")),
                ("description", models.TextField(blank=True, default="", verbose_name="Описание")),
                ("description_ru", models.TextField(blank=True, default="", null=True, verbose_name="Описание")),
                ("description_en", models.TextField(blank=True, default="", null=True, verbose_name="Описание")),
                ("description_uz", models.TextField(blank=True, default="", null=True, verbose_name="Описание")),
                ("order", models.PositiveIntegerField(default=0, verbose_name="Порядок")),
                ("is_active", models.BooleanField(default=True, verbose_name="Активен")),
                ("hall", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="sections",
                    to="exhibit.hall",
                    verbose_name="Зал",
                )),
            ],
            options={
                "verbose_name": "Раздел",
                "verbose_name_plural": "Разделы",
                "ordering": ["order", "name"],
            },
        ),
        # 3. Add nullable section FK to Exhibit
        migrations.AddField(
            model_name="exhibit",
            name="section",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="exhibits",
                to="exhibit.section",
                verbose_name="Раздел",
            ),
        ),
        # 4. Migrate data
        migrations.RunPython(
            migrate_location_to_hall_section,
            migrations.RunPython.noop,
        ),
        # 5. Remove old location FK from Exhibit
        migrations.RemoveField(
            model_name="exhibit",
            name="location",
        ),
        # 6. Make section FK non-nullable
        migrations.AlterField(
            model_name="exhibit",
            name="section",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="exhibits",
                to="exhibit.section",
                verbose_name="Раздел",
            ),
        ),
        # 7. Delete Location table
        migrations.DeleteModel(
            name="Location",
        ),
    ]
