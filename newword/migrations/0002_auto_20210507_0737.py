# Generated by Django 3.2.2 on 2021-05-07 00:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newword', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='test',
            name='test_num',
        ),
        migrations.AlterField(
            model_name='test',
            name='score',
            field=models.FloatField(blank=True),
        ),
    ]
