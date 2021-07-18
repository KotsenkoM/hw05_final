# Generated by Django 2.2.6 on 2021-07-18 06:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0008_auto_20210718_0506'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='follow',
            name='unique',
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(fields=('user', 'author'), name='unique_follows'),
        ),
    ]