# Generated by Django 5.1.3 on 2024-11-16 21:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatgpt', '0003_comida_calorias_alter_comida_descripcion_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='comida',
            name='carbohidratos',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='comida',
            name='grasas',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='comida',
            name='proteinas',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
