# Generated by Django 5.1.6 on 2025-03-01 05:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0007_rename_course_name_trainingsession_session_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='trainingsession',
            old_name='session_name',
            new_name='course_name',
        ),
    ]
