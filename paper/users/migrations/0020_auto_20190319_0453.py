# Generated by Django 2.0.10 on 2019-03-19 04:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0019_auto_20190317_2107'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='description',
            field=models.CharField(blank=True, max_length=3000),
        ),
    ]
