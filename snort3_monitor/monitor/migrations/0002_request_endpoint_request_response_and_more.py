# Generated by Django 4.2.7 on 2023-12-11 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='endpoint',
            field=models.CharField(default='', max_length=128),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='request',
            name='response',
            field=models.IntegerField(default=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='request',
            name='user_addr',
            field=models.CharField(max_length=50),
        ),
    ]
