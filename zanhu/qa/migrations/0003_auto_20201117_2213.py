# Generated by Django 3.1.3 on 2020-11-17 14:13

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('qa', '0002_auto_20201116_2105'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vote',
            name='uuid',
            field=models.UUIDField(default=uuid.UUID('2e579ba6-b854-4647-8758-2c387878ad3b'), editable=False, primary_key=True, serialize=False),
        ),
    ]
