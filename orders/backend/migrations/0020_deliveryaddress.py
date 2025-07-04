# Generated by Django 5.2 on 2025-06-09 13:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0019_remove_user_lastname_remove_user_name_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.CharField(max_length=50)),
                ('street', models.CharField(max_length=100)),
                ('building', models.CharField(max_length=10)),
                ('block', models.CharField(blank=True, max_length=10, null=True)),
                ('structure', models.CharField(blank=True, max_length=10, null=True)),
                ('apartment', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User delivery address',
                'verbose_name_plural': 'Users delivery addresses',
            },
        ),
    ]
