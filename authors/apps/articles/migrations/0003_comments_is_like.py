# Generated by Django 2.1.3 on 2019-01-31 10:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0002_auto_20190131_0930'),
    ]

    operations = [
        migrations.AddField(
            model_name='comments',
            name='is_like',
            field=models.BooleanField(default=False),
        ),
    ]
