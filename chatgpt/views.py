from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Comida, Categoria
from .serializers import ComidaSerializer, CategoriaSerializer
from django.conf import settings
import openai
import datetime
import requests

class ComidaList(APIView):
    def get(self, request):
        comidas = Comida.objects.filter(disponible=True)
        serializer = ComidaSerializer(comidas, many=True)
        return Response(serializer.data)

class CategoriaList(APIView):
    def get(self, request):
        categorias = Categoria.objects.all()
        serializer = CategoriaSerializer(categorias, many=True)
        return Response(serializer.data)

class ChatbotView(APIView):
    def post(self, request):
        try:
            user_input = request.data.get('message')
            if not user_input:
                return Response({'error': 'No se proporcionó un mensaje'}, status=400)

            if not getattr(settings, 'OPENAI_API_KEY', None):
                return Response({'error': 'Clave de API de OpenAI no configurada'}, status=500)

            # Obtener datos de comidas disponibles
            comidas = Comida.objects.filter(disponible=True).select_related('categoria')
            if not comidas.exists():
                return Response({'error': 'No hay comidas disponibles'}, status=404)

            # Información de las comidas
            comidas_info = []
            categorias_dict = {}

            for comida in comidas:
                # Modificar el nombre de la comida para mejorar la precisión
                nombre_comida = self.obtener_nombre_comida_para_api(comida.nombre)

                # Obtener información nutricional desde Edamam
                nutricion = self.obtener_info_nutricional(nombre_comida)
                if nutricion:
                    calorias = nutricion.get('calories', 'No disponible')
                    nutrientes = nutricion.get('totalNutrients', {})
                    proteinas = nutrientes.get('PROCNT', {}).get('quantity', 'No disponible')
                    grasas = nutrientes.get('FAT', {}).get('quantity', 'No disponible')
                    carbohidratos = nutrientes.get('CHOCDF', {}).get('quantity', 'No disponible')
                else:
                    calorias = proteinas = grasas = carbohidratos = 'No disponible'

                comida_data = {
                    'nombre': comida.nombre,
                    'puntuacion': comida.puntuacion,
                    'categoria': comida.categoria.nombre,
                    'calorias': f"{calorias} kcal" if calorias != 'No disponible' else calorias,
                    'descripcion': comida.descripcion or 'Sin descripción',
                    'nutrientes': {
                        'proteinas': f"{proteinas:.1f} g" if isinstance(proteinas, (int, float)) else proteinas,
                        'grasas': f"{grasas:.1f} g" if isinstance(grasas, (int, float)) else grasas,
                        'carbohidratos': f"{carbohidratos:.1f} g" if isinstance(carbohidratos, (int, float)) else carbohidratos,
                    },
                }
                comidas_info.append(comida_data)

                # Mejor puntuación por categoría
                categoria_nombre = comida.categoria.nombre
                if categoria_nombre not in categorias_dict or comida.puntuacion > categorias_dict[categoria_nombre]['puntuacion']:
                    categorias_dict[categoria_nombre] = comida_data

            # Formatear texto para el chatbot
            comidas_texto = ""
            for comida in comidas_info:
                estrellas = '★' * comida['puntuacion'] + '☆' * (5 - comida['puntuacion'])
                comidas_texto += f"### {comida['nombre']} ({comida['categoria']})\n"
                comidas_texto += f"- **Puntuación:** {estrellas}\n"
                comidas_texto += f"- **Calorías:** {comida['calorias']}\n"
                comidas_texto += f"- **Nutrientes:**\n"
                comidas_texto += f"  - Proteínas: {comida['nutrientes']['proteinas']}\n"
                comidas_texto += f"  - Grasas: {comida['nutrientes']['grasas']}\n"
                comidas_texto += f"  - Carbohidratos: {comida['nutrientes']['carbohidratos']}\n"
                comidas_texto += f"- **Descripción:** {comida['descripcion']}\n\n"

            # Información de las mejores comidas por categoría
            mejores_comidas_texto = ""
            for categoria, datos in categorias_dict.items():
                estrellas = '★' * datos['puntuacion'] + '☆' * (5 - datos['puntuacion'])
                mejores_comidas_texto += f"- **{categoria}:** {datos['nombre']} con puntuación de {estrellas}\n"

            fecha_actual = datetime.datetime.now().strftime("%d/%m/%Y")

            # Analizar si el usuario solicita una tabla calórica
            solicita_tabla_calorica = any(keyword in user_input.lower() for keyword in ['tabla calórica', 'tabla calorica', 'tabla de calorías', 'tabla de calorias'])

            if solicita_tabla_calorica:
                # Crear una tabla calórica detallada
                tabla_calorica = (
                    "| **Comida**           | **Calorías**   | **Proteínas**   | **Grasas**      | **Carbohidratos** |\n"
                    "|----------------------|---------------:|----------------:|----------------:|------------------:|\n"
                )
                for comida in comidas_info:
                    tabla_calorica += (
                        f"| {comida['nombre']:<20} | {comida['calorias']:<13} | "
                        f"{comida['nutrientes']['proteinas']:<14} | {comida['nutrientes']['grasas']:<14} | "
                        f"{comida['nutrientes']['carbohidratos']:<17} |\n"
                    )

                assistant_response = f"### Tabla Calórica de Comidas Disponibles\n\n{tabla_calorica}"
                return Response({'response': assistant_response})

            else:
                # Crear el mensaje para la IA
                system_prompt = (
                    "Eres un asistente culinario experto que ayuda a los usuarios brindando información detallada sobre las comidas disponibles. "
                    "Cuando proporciones información, organiza los datos de manera clara y estructurada usando Markdown. "
                    "Incluye tablas si es necesario y utiliza listas y encabezados para separar secciones. "
                    "Muestra las puntuaciones utilizando estrellas (★) y proporciona información nutricional cuando esté disponible. "
                    "Si no dispones de cierta información, indícalo claramente al usuario."
                )

                context = (
                    f"Fecha actual: {fecha_actual}\n\n"
                    f"Comidas disponibles:\n{comidas_texto}\n"
                    f"Mejores comidas por categoría:\n{mejores_comidas_texto}\n"
                )

                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "assistant", "content": context},
                    {"role": "user", "content": user_input},
                ]

                openai.api_key = settings.OPENAI_API_KEY
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    max_tokens=700,
                    temperature=0.7,
                )

                assistant_response = response.choices[0].message['content'].strip()
                return Response({'response': assistant_response})

        except openai.OpenAIError as e:
            return Response({'error': f'Error de OpenAI: {str(e)}'}, status=500)
        except Exception as e:
            return Response({'error': f'Error al procesar la solicitud: {str(e)}'}, status=500)

    def obtener_info_nutricional(self, nombre_comida):
        try:
            url = 'https://api.edamam.com/api/nutrition-data'
            # Incluir una cantidad y unidad para mejorar la precisión
            ingr = f"1 serving {nombre_comida}"
            params = {
                'app_id': settings.EDAMAM_APP_ID,
                'app_key': settings.EDAMAM_APP_KEY,
                'ingr': ingr,
            }
            response = requests.get(url, params=params)
            data = response.json()
            if response.status_code == 200 and data.get('calories') and data.get('totalNutrients'):
                return data
            else:
                return None
        except Exception as e:
            print(f"Error al obtener información nutricional: {e}")
            return None

    def obtener_nombre_comida_para_api(self, nombre_comida):
        # Mapeo de nombres de platos a ingredientes reconocidos por la API
        mapping = {
            'causa': 'potato with tuna',
            'arroz con leche': 'rice pudding',
            'gelatina': 'gelatin dessert',
            'flan': 'custard',
            'pan con pollo': 'chicken sandwich',
            'pan con queso': 'cheese sandwich',
            'chicharron de pollo': 'fried chicken',
        }
        return mapping.get(nombre_comida.lower(), nombre_comida)
