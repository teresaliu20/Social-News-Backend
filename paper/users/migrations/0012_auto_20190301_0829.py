# Generated by Django 2.0.10 on 2019-03-01 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_collection_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='linksAccepted',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='user',
            name='linksProposed',
            field=models.IntegerField(default=0),
        ),
    ]
