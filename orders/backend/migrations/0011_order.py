# Generated by Django 5.2 on 2025-04-28 20:06

import django.db.models.deletion
import django.db.models.manager
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0010_alter_parameter_options_alter_parameter_name_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.IntegerField(choices=[(1, 'Created'), (2, 'Paid'), (3, 'Processing'), (4, 'Dispatched'), (5, 'In Transit'), (6, 'Delivered'), (7, 'Cancelled')], default=1)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Order',
                'verbose_name_plural': 'Orders',
            },
            managers=[
                ('orders', django.db.models.manager.Manager()),
            ],
        ),
    ]
