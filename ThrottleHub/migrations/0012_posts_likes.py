# Generated by Django 4.2.10 on 2024-04-16 09:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ERP', '0011_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='posts',
            name='likes',
            field=models.IntegerField(default=0),
        ),
    ]
