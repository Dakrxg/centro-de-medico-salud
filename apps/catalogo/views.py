from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import PrestacionForm
from .models import EspecialidadMedica, PrestacionMedica

ORDENES = {
    'nombre_asc': 'nombre',
    'arancel_asc': 'arancel',
    'arancel_desc': '-arancel',
    'duracion': 'duracion_minutos',
}


def es_administrador(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


# Rutas administrativas: @login_required + @solo_staff
solo_staff = user_passes_test(es_administrador, login_url='core:sin_permiso')


# ---------------------------------------------------------------- Público (R)
def prestacion_lista(request):
    query = request.GET.get('q', '').strip()
    especialidad_slug = request.GET.get('especialidad', '')
    orden = request.GET.get('orden', 'nombre_asc')

    prestaciones = PrestacionMedica.objects.filter(
        vigente=True, especialidad__activa=True).select_related('especialidad')

    if especialidad_slug:
        prestaciones = prestaciones.filter(especialidad__slug=especialidad_slug)

    if query:
        prestaciones = prestaciones.filter(
            Q(nombre__icontains=query) | Q(codigo__icontains=query) | Q(descripcion__icontains=query))

    prestaciones = prestaciones.order_by(ORDENES.get(orden, 'nombre'))
    total_resultados = prestaciones.count()

    pagina = Paginator(prestaciones, 6).get_page(request.GET.get('page'))
    parametros = request.GET.copy()
    parametros.pop('page', None)

    especialidades = EspecialidadMedica.objects.filter(activa=True).annotate(
        total=Count('prestaciones', filter=Q(prestaciones__vigente=True)))

    return render(request, 'catalogo/prestacion_lista.html', {
        'prestaciones': pagina,
        'especialidades': especialidades,
        'especialidad_sel': especialidad_slug,
        'query_actual': query,
        'orden_actual': orden,
        'total_resultados': total_resultados,
        'querystring': parametros.urlencode(),
    })


def prestacion_detalle(request, slug):
    prestacion = get_object_or_404(
        PrestacionMedica.objects.select_related('especialidad'), slug=slug)
    if not prestacion.vigente and not es_administrador(request.user):
        raise Http404('Prestación no disponible.')
    relacionadas = PrestacionMedica.objects.filter(
        especialidad=prestacion.especialidad, vigente=True
    ).exclude(pk=prestacion.pk).select_related('especialidad')[:3]
    return render(request, 'catalogo/prestacion_detalle.html', {
        'p': prestacion, 'relacionadas': relacionadas})


# ------------------------------------------------------------ Backoffice (CRUD)
@login_required
@solo_staff
def gestion_prestaciones(request):
    query = request.GET.get('q', '').strip()
    prestaciones = PrestacionMedica.objects.select_related('especialidad')
    if query:
        prestaciones = prestaciones.filter(
            Q(nombre__icontains=query) | Q(codigo__icontains=query) | Q(descripcion__icontains=query))
    pagina = Paginator(prestaciones, 10).get_page(request.GET.get('page'))
    return render(request, 'catalogo/gestion_prestaciones.html', {'prestaciones': pagina, 'query': query})


@login_required
@solo_staff
def prestacion_crear(request):
    form = PrestacionForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        prestacion = form.save()
        messages.success(request, f"Prestación '{prestacion.nombre}' creada correctamente.")
        return redirect('catalogo:gestion')
    return render(request, 'catalogo/prestacion_form.html', {
        'form': form, 'titulo_accion': 'Ingresar Nueva Prestación', 'boton_texto': 'Guardar'})


@login_required
@solo_staff
def prestacion_editar(request, slug):
    prestacion = get_object_or_404(PrestacionMedica, slug=slug)
    form = PrestacionForm(request.POST or None, request.FILES or None, instance=prestacion)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f"Prestación '{prestacion.nombre}' actualizada.")
        return redirect('catalogo:gestion')
    return render(request, 'catalogo/prestacion_form.html', {
        'form': form, 'p': prestacion, 'titulo_accion': 'Editar Prestación', 'boton_texto': 'Actualizar'})


@login_required
@solo_staff
def prestacion_eliminar(request, slug):
    """Pantalla de confirmación + baja lógica (no se borra físicamente)."""
    prestacion = get_object_or_404(PrestacionMedica, slug=slug)
    if request.method == 'POST':
        prestacion.vigente = False
        prestacion.save(update_fields=['vigente', 'fecha_actualizacion'])
        messages.warning(request, f"'{prestacion.nombre}' fue dada de baja (puedes reactivarla).")
        return redirect('catalogo:gestion')
    return render(request, 'catalogo/prestacion_confirmar_baja.html', {'p': prestacion})


@login_required
@solo_staff
@require_POST
def prestacion_reactivar(request, slug):
    prestacion = get_object_or_404(PrestacionMedica, slug=slug)
    prestacion.vigente = True
    prestacion.save(update_fields=['vigente', 'fecha_actualizacion'])
    messages.success(request, f"'{prestacion.nombre}' fue reactivada.")
    return redirect('catalogo:gestion')
