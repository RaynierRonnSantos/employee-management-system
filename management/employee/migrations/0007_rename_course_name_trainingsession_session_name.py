# Generated by Django 5.1.6 on 2025-03-01 05:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0006_trainingsession'),
    ]

    operations = [
        migrations.RenameField(
            model_name='trainingsession',
            old_name='course_name',
            new_name='session_name',
        ),
    ]
