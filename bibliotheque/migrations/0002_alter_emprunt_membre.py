# Generated by Django 5.1.6 on 2025-02-18 09:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bibliotheque", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="emprunt",
            name="membre",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="emprunts",
                to="bibliotheque.membre",
            ),
        ),
    ]
