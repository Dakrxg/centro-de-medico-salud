from django.db.models import Count, Q
from django.shortcuts import render

from apps.catalogo.models import EspecialidadMedica, PrestacionMedica


def inicio(request):
    """Portada: prestaciones destacadas y especialidades con su cantidad de prestaciones."""
    destacadas = PrestacionMedica.objects.filter(
        vigente=True, destacada=True, especialidad__activa=True
    ).select_related('especialidad')[:4]

    especialidades = EspecialidadMedica.objects.filter(activa=True).annotate(
        total=Count('prestaciones', filter=Q(prestaciones__vigente=True)))

    return render(request, 'core/inicio.html', {
        'destacadas': destacadas,
        'especialidades': especialidades,
        'total_prestaciones': PrestacionMedica.objects.filter(vigente=True).count(),
        'total_especialidades': especialidades.count(),
    })


def nosotros(request):
    """Información institucional del centro médico."""
    return render(request, 'core/nosotros.html')


def sin_permiso(request):
    """Destino de @user_passes_test cuando el usuario no tiene rol staff."""
    return render(request, 'core/sin_permiso.html', status=403)
