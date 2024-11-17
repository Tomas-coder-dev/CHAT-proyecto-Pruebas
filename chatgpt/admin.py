# chatgpt/admin.py

from django.contrib import admin
from .models import Comida, Categoria

@admin.register(Comida)
class ComidaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'puntuacion', 'disponible')
    list_filter = ('categoria', 'disponible')
    search_fields = ('nombre', 'descripcion')

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)
