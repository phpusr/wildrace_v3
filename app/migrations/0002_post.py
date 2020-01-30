# Generated by Django 3.0.2 on 2020-01-30 09:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(1, 'Success'), (2, 'Error Sum'), (3, 'Error Parse'), (4, 'Error Start Sum')])),
                ('date', models.DateTimeField()),
                ('number', models.IntegerField()),
                ('text', models.TextField()),
                ('text_hash', models.CharField(max_length=32)),
                ('distance', models.IntegerField(blank=True, null=True)),
                ('sum_distance', models.IntegerField(blank=True, null=True)),
                ('edit_reason', models.CharField(blank=True, max_length=255, null=True)),
                ('last_update', models.DateTimeField(blank=True, null=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.Profile')),
            ],
        ),
    ]
