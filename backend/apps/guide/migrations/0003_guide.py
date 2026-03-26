from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('guide', '0002_rule_content_en_rule_content_ru_rule_content_uz_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Guide',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Имя')),
                ('description', models.TextField(blank=True, default='', verbose_name='Описание')),
                ('video', models.FileField(blank=True, null=True, upload_to='guides/videos/', verbose_name='Видео')),
                ('thumbnail', models.ImageField(blank=True, null=True, upload_to='guides/thumbnails/', verbose_name='Превью')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Порядок')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активен')),
            ],
            options={
                'verbose_name': 'Гид',
                'verbose_name_plural': 'Гиды',
                'ordering': ['order', 'name'],
            },
        ),
    ]
