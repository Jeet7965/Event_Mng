# Generated by Django 5.2 on 2025-05-05 10:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0029_chathistory_qapair'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventtype',
            name='cost',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='eventtype',
            name='example_data',
            field=models.TextField(blank=True, null=True),
        ),
    ]
