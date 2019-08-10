# Generated by Django 2.1.7 on 2019-08-05 20:38

import annotator.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annotator', '0003_auto_20190805_2004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='audioannotation',
            name='audio',
            field=models.FileField(help_text='An audio file for the segment', upload_to=annotator.models.user_directory_path),
        ),
    ]