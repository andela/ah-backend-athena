# Generated by Django 2.1.3 on 2019-01-31 11:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0003_comments_is_like'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comments',
            name='is_like',
        ),
    ]
