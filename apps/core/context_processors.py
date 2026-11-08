from django.conf import settings


def organizacion(request):
    """Expone el nombre de la organización a todas las plantillas."""
    return {'NOMBRE_ORGANIZACION': settings.NOMBRE_ORGANIZACION}
