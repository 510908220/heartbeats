# Generated by Django 2.0.3 on 2018-03-13 06:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='service',
            name='owner',
        ),
    ]
