# chatgpt/models.py

from django.db import models

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Comida(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(null=True, blank=True)
    puntuacion = models.IntegerField()
    disponible = models.BooleanField(default=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    calorias = models.IntegerField(null=True, blank=True)
    proteinas = models.FloatField(null=True, blank=True)
    grasas = models.FloatField(null=True, blank=True)
    carbohidratos = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.nombre
