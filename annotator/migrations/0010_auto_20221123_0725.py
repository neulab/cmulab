# Generated by Django 2.1.5 on 2022-11-23 07:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annotator', '0009_userprofile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mlmodel',
            name='status',
            field=models.CharField(choices=[('queued', 'queued'), ('training', 'training'), ('ready', 'ready'), ('unavailable', 'unavailable')], default='unavailable', max_length=20),
        ),
    ]
