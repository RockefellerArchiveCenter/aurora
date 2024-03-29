# Generated by Django 4.0.7 on 2022-09-06 20:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag_transfer', '0042_user_token'),
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('is_application', models.BooleanField(default=True)),
                ('is_authenticated', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=100)),
                ('client_id', models.CharField(max_length=50)),
            ],
        ),
    ]
