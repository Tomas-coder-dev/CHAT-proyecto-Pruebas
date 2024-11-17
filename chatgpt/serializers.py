from rest_framework import serializers
from .models import Comida, Categoria

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre']

class ComidaSerializer(serializers.ModelSerializer):
    categoria = CategoriaSerializer(read_only=True)

    class Meta:
        model = Comida
        fields = [
            'id',
            'nombre',
            'descripcion',
            'puntuacion',
            'disponible',
            'categoria',
            'calorias',
            'proteinas',
            'grasas',
            'carbohidratos',
        ]
