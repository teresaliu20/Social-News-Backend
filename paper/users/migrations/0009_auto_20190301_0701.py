# Generated by Django 2.0.10 on 2019-03-01 07:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_auto_20190301_0646'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Bookmark',
            new_name='Link',
        ),
    ]
