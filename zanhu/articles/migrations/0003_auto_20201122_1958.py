# Generated by Django 2.1.7 on 2020-11-22 11:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0002_auto_20201115_1907'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='创建时间'),
        ),
    ]
