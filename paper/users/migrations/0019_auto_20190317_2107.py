# Generated by Django 2.0.10 on 2019-03-17 21:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_auto_20190317_0141'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Tag',
            new_name='Topic',
        ),
    ]
