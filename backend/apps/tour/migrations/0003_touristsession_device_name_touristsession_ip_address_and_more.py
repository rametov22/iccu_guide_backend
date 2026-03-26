# Custom migration: UUID device_token → PositiveIntegerField + new fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tour', '0002_tourrating'),
    ]

    operations = [
        # 1. Add new fields
        migrations.AddField(
            model_name='touristsession',
            name='device_name',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Название устройства'),
        ),
        migrations.AddField(
            model_name='touristsession',
            name='ip_address',
            field=models.GenericIPAddressField(blank=True, null=True, verbose_name='IP-адрес'),
        ),
        migrations.AddField(
            model_name='touristsession',
            name='tour_number',
            field=models.PositiveIntegerField(blank=True, help_text='Порядковый номер присоединения к туру', null=True, verbose_name='Номер в туре'),
        ),
        # 2. Remove old UUID device_token column and re-add as integer
        migrations.RemoveField(
            model_name='touristsession',
            name='device_token',
        ),
        migrations.AddField(
            model_name='touristsession',
            name='device_token',
            field=models.PositiveIntegerField(default=0, help_text='Число от 1 до 600', unique=True, verbose_name='Номер устройства'),
            preserve_default=False,
        ),
    ]
