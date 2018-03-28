# Generated by Django 2.0.3 on 2018-03-19 05:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_auto_20180313_0751'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('remote_addr', models.GenericIPAddressField(blank=True, null=True)),
                ('ua', models.CharField(blank=True, max_length=200)),
                ('data', models.TextField(blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pings', to='app.Service')),
            ],
            options={
                'db_table': 'ping',
            },
        ),
    ]
