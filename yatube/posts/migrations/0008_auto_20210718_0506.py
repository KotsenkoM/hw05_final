# Generated by Django 2.2.6 on 2021-07-18 05:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_follow'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(fields=('user',), name='unique'),
        ),
    ]
