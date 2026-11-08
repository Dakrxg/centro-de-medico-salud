from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import LoginForm, RegistroForm


def registro_usuario(request):
    if request.user.is_authenticated:
        return redirect('catalogo:lista')
    form = RegistroForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f'¡Bienvenido/a, {user.first_name}! Tu cuenta fue creada.')
        return redirect('catalogo:lista')
    return render(request, 'usuarios/registro.html', {'form': form})


def login_usuario(request):
    if request.user.is_authenticated:
        return redirect('catalogo:lista')
    siguiente = request.POST.get('next') or request.GET.get('next', '')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        messages.success(request, 'Sesión iniciada correctamente.')
        # Evita "open redirect": solo se aceptan destinos del mismo sitio
        if siguiente and url_has_allowed_host_and_scheme(siguiente, allowed_hosts={request.get_host()}):
            return redirect(siguiente)
        return redirect('catalogo:lista')
    return render(request, 'usuarios/login.html', {'form': form, 'next': siguiente})


@require_POST  # el cierre de sesión se hace por POST + CSRF
def logout_usuario(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión.')
    return redirect('core:inicio')


@login_required
def perfil_usuario(request):
    perfil = getattr(request.user, 'perfil', None)
    return render(request, 'usuarios/perfil.html', {'usuario': request.user, 'perfil': perfil})
