# Generated by Django 2.0.10 on 2019-03-03 04:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_auto_20190301_0829'),
    ]

    operations = [
        migrations.CreateModel(
            name='CollectionRelationship',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('relationship', models.CharField(blank=True, choices=[('Explains', 'explains'), ('Opposes', 'opposes'), ('Subcategory', 'is subcategory of')], max_length=10)),
                ('approved', models.BooleanField(default=False)),
            ],
        ),
        migrations.RemoveField(
            model_name='feedsubscription',
            name='subscriber',
        ),
        migrations.RenameField(
            model_name='collection',
            old_name='creator',
            new_name='owner',
        ),
        migrations.DeleteModel(
            name='FeedSubscription',
        ),
        migrations.AddField(
            model_name='collectionrelationship',
            name='end',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='endpoint', to='users.Collection'),
        ),
        migrations.AddField(
            model_name='collectionrelationship',
            name='start',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='origin', to='users.Collection'),
        ),
    ]
