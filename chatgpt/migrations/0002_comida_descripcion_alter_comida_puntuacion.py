# Generated by Django 5.1.3 on 2024-11-16 06:59

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatgpt', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='comida',
            name='descripcion',
            field=models.TextField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='comida',
            name='puntuacion',
            field=models.DecimalField(decimal_places=1, max_digits=3),
        ),
    ]
