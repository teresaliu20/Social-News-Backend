# Generated by Django 2.0.10 on 2019-02-13 19:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_feedsubscription'),
    ]

    operations = [
        migrations.RenameField(
            model_name='feedsubscription',
            old_name='link',
            new_name='rss_link',
        ),
    ]
