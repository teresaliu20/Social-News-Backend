# Generated by Django 2.0.10 on 2019-03-01 07:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_auto_20190301_0701'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='description',
            field=models.CharField(blank=True, max_length=500),
        ),
    ]
