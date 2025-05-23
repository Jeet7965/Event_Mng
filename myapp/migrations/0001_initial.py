# Generated by Django 5.2 on 2025-04-22 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CateringOption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Venue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('venue_type', models.CharField(choices=[('hall', 'Hall'), ('hotel', 'Hotel'), ('lawn', 'Lawn')], max_length=10)),
                ('location', models.CharField(max_length=255)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('capacity', models.IntegerField()),
                ('catering', models.ManyToManyField(to='myapp.cateringoption')),
            ],
        ),
    ]
