# Generated by Django 3.0.6 on 2020-05-28 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_auto_20200528_1656'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=122)),
                ('header', models.CharField(max_length=122)),
                ('desc', models.TextField()),
            ],
        ),
        migrations.DeleteModel(
            name='Events',
        ),
    ]
