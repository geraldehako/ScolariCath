# Generated by Django 4.2.2 on 2025-05-04 12:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("eleves", "0002_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="eleves",
            name="matricule",
            field=models.CharField(blank=True, max_length=9, unique=True),
        ),
    ]
