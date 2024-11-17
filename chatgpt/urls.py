# chatgpt/urls.py

from django.urls import path
from .views import ChatbotView, ComidaList, CategoriaList

urlpatterns = [
    path('chatbot/', ChatbotView.as_view(), name='chatbot'),
    path('comidas/', ComidaList.as_view(), name='comida-list'),
    path('categorias/', CategoriaList.as_view(), name='categoria-list'),
]
