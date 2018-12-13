# Generated by Django 2.1.3 on 2018-12-12 16:34

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Follow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('followed', models.IntegerField()),
                ('follower', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
