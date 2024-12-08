# Generated by Django 5.1.3 on 2024-12-08 20:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0013_alter_profile_major'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='following',
            field=models.ManyToManyField(blank=True, related_name='followers', to='home.profile'),
        ),
        migrations.AddField(
            model_name='profile',
            name='picture',
            field=models.URLField(blank=True, default='/static/img/logo-new.png', help_text="URL to the user's profile picture", null=True),
        ),
    ]