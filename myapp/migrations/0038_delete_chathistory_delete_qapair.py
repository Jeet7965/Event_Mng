# Generated by Django 5.2 on 2025-05-07 14:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0037_remove_service_catering'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ChatHistory',
        ),
        migrations.DeleteModel(
            name='QAPair',
        ),
    ]
