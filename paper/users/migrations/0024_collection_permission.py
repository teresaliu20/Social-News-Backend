# Generated by Django 2.0.10 on 2019-04-21 01:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0023_link_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='permission',
            field=models.CharField(blank=True, choices=[('Private', 'private'), ('Public', 'public'), ('Network', 'network')], max_length=30),
        ),
    ]