# Generated by Django 5.2 on 2025-06-24 16:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classrooms', '0002_initial'),
        ('subscriptions', '0003_alter_plan_created_at_alter_plan_description_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscriptiondetail',
            name='classroom',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subscription_details_for_classroom', to='classrooms.classroom'),
        ),
        migrations.AlterField(
            model_name='subscriptiondetail',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subscription_details_for_group', to='classrooms.group'),
        ),
    ]
