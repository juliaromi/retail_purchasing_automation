# Generated by Django 5.2 on 2025-04-28 14:26

import django.db.models.manager
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0008_rename_product_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='Parameter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name': 'Product parameter',
                'verbose_name_plural': 'Product parameters',
            },
            managers=[
                ('parameters', django.db.models.manager.Manager()),
            ],
        ),
    ]
