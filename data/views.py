from .models import Cliente
# Create your views here.

def save_to_db(client_obj):
    Cliente.objects.create(
        ci = client_obj['ci'],
        nombre = client_obj['nombre'],
        primer_apellido = client_obj['primer_apellido'],
        segundo_apellido = client_obj['segundo_apellido'],
        tipo_entrenamiento = client_obj['tipo_entrenamiento'],
        foto = client_obj['foto']
    )
