# Generated by Django 4.2.10 on 2024-04-18 04:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ERP', '0013_remove_posts_likes_likes'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profilepics',
            old_name='images',
            new_name='image',
        ),
    ]