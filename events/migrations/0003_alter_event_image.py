# Generated by Django 4.1.1 on 2022-09-10 20:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0002_event_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="image",
            field=models.ImageField(null=True, upload_to="event/images/"),
        ),
    ]
