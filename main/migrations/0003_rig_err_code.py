# Generated by Django 3.2.12 on 2022-06-24 10:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20220615_1242'),
    ]

    operations = [
        migrations.AddField(
            model_name='rig',
            name='err_code',
            field=models.IntegerField(null=True),
        ),
    ]
