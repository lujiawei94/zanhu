# Generated by Django 3.1.3 on 2020-11-16 13:05

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('qa', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='answer',
            old_name='uudi_id',
            new_name='uuid_id',
        ),
        migrations.AlterField(
            model_name='vote',
            name='uuid',
            field=models.UUIDField(default=uuid.UUID('feb007e6-9509-41ae-a67b-958e88a5636c'), editable=False, primary_key=True, serialize=False),
        ),
    ]
