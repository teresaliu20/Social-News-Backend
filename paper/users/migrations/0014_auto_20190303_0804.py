# Generated by Django 2.0.10 on 2019-03-03 08:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_auto_20190303_0404'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collectionrelationship',
            name='relationship',
            field=models.CharField(blank=True, choices=[('Explains', 'explains'), ('Opposes', 'opposes'), ('Subcategory', 'is subcategory of')], max_length=30),
        ),
    ]
