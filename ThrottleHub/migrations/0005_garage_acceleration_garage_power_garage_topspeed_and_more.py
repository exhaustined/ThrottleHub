# Generated by Django 4.2.10 on 2024-04-11 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ERP', '0004_garage_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='garage',
            name='acceleration',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='garage',
            name='power',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='garage',
            name='topspeed',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='garage',
            name='torque',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='garage',
            name='weight',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
