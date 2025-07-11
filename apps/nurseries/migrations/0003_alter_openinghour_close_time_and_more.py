# Generated by Django 5.2 on 2025-06-11 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nurseries', '0002_alter_nursery_manager'),
    ]

    operations = [
        migrations.AlterField(
            model_name='openinghour',
            name='close_time',
            field=models.TimeField(blank=True, help_text='Heure de fermeture (HH:MM)', null=True),
        ),
        migrations.AlterField(
            model_name='openinghour',
            name='open_time',
            field=models.TimeField(blank=True, help_text="Heure d'ouverture (HH:MM)", null=True),
        ),
    ]
