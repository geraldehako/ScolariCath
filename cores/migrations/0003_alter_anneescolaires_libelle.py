# Generated by Django 4.2.2 on 2025-05-04 16:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cores", "0002_cycles_code"),
    ]

    operations = [
        migrations.AlterField(
            model_name="anneescolaires",
            name="libelle",
            field=models.CharField(max_length=11, unique=True),
        ),
    ]
