# Generated by Django 5.2 on 2025-04-26 08:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0020_booking_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='user',
        ),
    ]
