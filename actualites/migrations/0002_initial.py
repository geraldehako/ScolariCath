# Generated by Django 4.2.2 on 2025-05-03 19:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("actualites", "0001_initial"),
        ("etablissements", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="actualites",
            name="etablissement",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="etablissements.etablissements",
            ),
        ),
    ]
