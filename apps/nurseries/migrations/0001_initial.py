# Generated by Django 5.2 on 2025-06-11 10:51

import apps.nurseries.models
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('classrooms', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Nursery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('upload_folder', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Dossier média unique attribué à chaque crèche', unique=True)),
                ('name', models.CharField(help_text='Nom de la crèche', max_length=255)),
                ('address', models.TextField(help_text='Adresse de la crèche')),
                ('contact_number', models.CharField(help_text='Téléphone de la crèche', max_length=15)),
                ('information', models.TextField(help_text='Informations complémentaires')),
                ('max_age', models.PositiveIntegerField(help_text='Âge maximum des enfants acceptés (en mois)')),
                ('max_children_per_class', models.PositiveIntegerField(help_text="Nombre maximum d'enfants par classe")),
                ('legal_status', models.CharField(choices=[('agrée', 'Agrée par le ministère'), ('en_cours', 'En cours d’agrément'), ('communautaire', 'Structure communautaire'), ('autre', 'Autre')], default='en_cours', help_text='Statut légal de la structure', max_length=20)),
                ('agreement_document', models.FileField(blank=True, help_text='Document d’agrément (PDF, image)', null=True, upload_to=apps.nurseries.models.doc_upload_path)),
                ('id_card_document', models.FileField(blank=True, help_text='Pièce d’identité du responsable', null=True, upload_to=apps.nurseries.models.doc_upload_path)),
                ('photo_exterior', models.ImageField(blank=True, help_text='Photo extérieure de la crèche', null=True, upload_to=apps.nurseries.models.images_upload_path)),
                ('photo_interior', models.ImageField(blank=True, help_text='Photo intérieure de la crèche', null=True, upload_to=apps.nurseries.models.images_upload_path)),
                ('verified', models.BooleanField(default=False, help_text='Indique si la crèche est certifiée par la plateforme')),
                ('online', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Date de création')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Date de dernière mise à jour')),
                ('manager', models.OneToOneField(help_text="Manager (UserType avec le rôle 'nursery_manager')", limit_choices_to={'type': 'nursery_manager'}, on_delete=django.db.models.deletion.CASCADE, related_name='managed_nurseries', to='users.usertype')),
            ],
            options={
                'verbose_name': 'Crèche',
                'verbose_name_plural': 'Crèches',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='NurseryAssistant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_manager', models.BooleanField(default=False, help_text='Rôle de manager temporaire ?')),
                ('active', models.BooleanField(default=True)),
                ('classroom', models.ForeignKey(blank=True, help_text="Classe dans laquelle l'assistant est assigné", null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assistants', to='classrooms.classroom')),
                ('group', models.ForeignKey(blank=True, help_text="Groupe d'enfants pris en charge", null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assistants', to='classrooms.group')),
                ('nursery', models.ForeignKey(help_text="Crèche dans laquelle l'assistant travaille", on_delete=django.db.models.deletion.CASCADE, related_name='assistants', to='nurseries.nursery')),
                ('profil', models.ForeignKey(help_text="Profil UserType de l'assistant", limit_choices_to={'type': 'nursery_assistant'}, on_delete=django.db.models.deletion.CASCADE, to='users.usertype')),
            ],
            options={
                'verbose_name': 'Assistant de crèche',
                'verbose_name_plural': 'Assistants de crèche',
                'unique_together': {('profil', 'nursery')},
            },
        ),
        migrations.CreateModel(
            name='OpeningHour',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.IntegerField(choices=[(0, 'Lundi'), (1, 'Mardi'), (2, 'Mercredi'), (3, 'Jeudi'), (4, 'Vendredi'), (5, 'Samedi'), (6, 'Dimanche')], help_text='Jour de la semaine (0=Lundi, …, 6=Dimanche)')),
                ('open_time', models.TimeField(help_text="Heure d'ouverture (HH:MM)")),
                ('close_time', models.TimeField(help_text='Heure de fermeture (HH:MM)')),
                ('is_closed', models.BooleanField(default=False, help_text='Si vrai, la crèche est fermée ce jour')),
                ('nursery', models.ForeignKey(help_text='Crèche liée à cet horaire', on_delete=django.db.models.deletion.CASCADE, related_name='opening_hours', to='nurseries.nursery')),
            ],
            options={
                'verbose_name': "Horaire d'ouverture",
                'verbose_name_plural': "Horaires d'ouverture",
                'ordering': ['day'],
                'unique_together': {('nursery', 'day')},
            },
        ),
    ]
