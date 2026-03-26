import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tour', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TourRating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveSmallIntegerField(
                    help_text='От 1 до 5 звёзд',
                    validators=[
                        django.core.validators.MinValueValidator(1),
                        django.core.validators.MaxValueValidator(5),
                    ],
                    verbose_name='Оценка',
                )),
                ('comment', models.TextField(blank=True, default='', verbose_name='Комментарий')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата')),
                ('tourist_session', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='rating',
                    to='tour.touristsession',
                    verbose_name='Сессия туриста',
                )),
            ],
            options={
                'verbose_name': 'Оценка тура',
                'verbose_name_plural': 'Оценки туров',
                'ordering': ['-created_at'],
            },
        ),
    ]
