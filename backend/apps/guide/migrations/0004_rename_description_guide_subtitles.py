from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('guide', '0003_guide'),
    ]

    operations = [
        migrations.RenameField(
            model_name='guide',
            old_name='description',
            new_name='subtitles',
        ),
    ]
