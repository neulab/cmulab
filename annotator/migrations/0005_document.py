# Generated by Django 2.1.5 on 2021-09-10 01:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annotator', '0004_auto_20190805_2038'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('docfile', models.FileField(upload_to='documents/%Y/%m/%d')),
            ],
        ),
    ]
