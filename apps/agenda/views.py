from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from apps.catalogo.models import PrestacionMedica
from apps.usuarios.models import PerfilUsuario

from .canasta import COBERTURA_PCT, Canasta


def _volver(request, defecto='agenda:ver'):
    siguiente = request.POST.get('next', '')
    if siguiente and url_has_allowed_host_and_scheme(siguiente, allowed_hosts={request.get_host()}):
        return redirect(siguiente)
    return redirect(defecto)


def _entero(valor, defecto=1):
    try:
        return int(valor)
    except (TypeError, ValueError):
        return defecto


def canasta_ver(request):
    contexto = Canasta(request).detalle()
    contexto['previsiones'] = [
        (valor, etiqueta, COBERTURA_PCT[valor]) for valor, etiqueta in PerfilUsuario.Prevision.choices]
    return render(request, 'agenda/canasta.html', contexto)


@require_POST
def canasta_agregar(request, pk):
    prestacion = get_object_or_404(PrestacionMedica.objects.select_related('especialidad'), pk=pk)
    ok, mensaje = Canasta(request).agregar(prestacion, _entero(request.POST.get('cantidad'), 1))
    (messages.success if ok else messages.error)(request, mensaje)
    return _volver(request, 'catalogo:lista')


@require_POST
def canasta_actualizar(request, pk):
    prestacion = get_object_or_404(PrestacionMedica, pk=pk)
    ok, mensaje = Canasta(request).actualizar(prestacion, _entero(request.POST.get('cantidad'), 0))
    (messages.success if ok else messages.error)(request, mensaje)
    return redirect('agenda:ver')


@require_POST
def canasta_quitar(request, pk):
    if Canasta(request).quitar(pk):
        messages.warning(request, 'Examen eliminado de tu canasta.')
    return redirect('agenda:ver')


@require_POST
def canasta_vaciar(request):
    Canasta(request).vaciar()
    messages.info(request, 'Tu canasta quedó vacía.')
    return redirect('agenda:ver')


@require_POST
def canasta_prevision(request):
    if Canasta(request).set_prevision(request.POST.get('prevision')):
        messages.success(request, 'Previsión actualizada; el copago fue recalculado.')
    else:
        messages.error(request, 'Previsión no válida.')
    return redirect('agenda:ver')


@login_required
@require_POST
def checkout_simulado(request):
    """Genera un comprobante simulado y vacía la canasta de la sesión."""
    canasta = Canasta(request)
    detalle = canasta.detalle()

    if not detalle['lineas']:
        messages.warning(request, 'Tu canasta está vacía.')
        return redirect('catalogo:lista')

    # Revalida disponibilidad y cupos justo antes de confirmar
    for linea in detalle['lineas']:
        p = linea['prestacion']
        if not p.disponible or linea['cantidad'] > p.cupos_diarios:
            messages.error(request, f"'{p.nombre}' ya no tiene disponibilidad suficiente. Revisa tu canasta.")
            return redirect('agenda:ver')

    ahora = timezone.localtime()
    folio = f'RSV-{ahora:%Y%m%d%H%M%S}-{request.user.pk}'
    canasta.vaciar()
    return render(request, 'agenda/comprobante.html', {
        **detalle, 'folio': folio, 'fecha': ahora, 'paciente': request.user})
