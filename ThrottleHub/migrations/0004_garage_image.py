# Generated by Django 4.2.10 on 2024-04-11 06:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ERP', '0003_alter_posts_owner_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='garage',
            name='image',
            field=models.ImageField(default=0, upload_to='images/'),
            preserve_default=False,
        ),
    ]
