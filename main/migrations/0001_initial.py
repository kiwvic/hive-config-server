# Generated by Django 3.2.12 on 2022-06-14 10:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Farm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Rig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_request', models.DateTimeField()),
                ('farm_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.farm')),
            ],
        ),
    ]
