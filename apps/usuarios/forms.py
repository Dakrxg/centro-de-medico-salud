from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.db import transaction

from apps.core.utils import aplicar_estilos_bootstrap

from .models import PerfilUsuario
from .validators import formatear_rut, validar_rut


class RegistroForm(UserCreationForm):
    first_name = forms.CharField(label='Nombres', max_length=150)
    last_name = forms.CharField(label='Apellidos', max_length=150)
    email = forms.EmailField(label='Correo electrónico')
    rut = forms.CharField(label='RUT', max_length=12, validators=[validar_rut],
                          help_text='Ej: 12.345.678-5')
    telefono = forms.CharField(label='Teléfono', max_length=20, required=False)
    prevision = forms.ChoiceField(label='Previsión', choices=PerfilUsuario.Prevision.choices)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        aplicar_estilos_bootstrap(self)

    def clean_rut(self):
        rut = formatear_rut(self.cleaned_data['rut'])
        if PerfilUsuario.objects.filter(rut=rut).exists():
            raise forms.ValidationError('Ya existe un usuario registrado con ese RUT.')
        return rut

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Este correo ya está registrado.')
        return email

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=True)
        PerfilUsuario.objects.create(
            user=user,
            rut=self.cleaned_data['rut'],
            telefono=self.cleaned_data['telefono'],
            prevision=self.cleaned_data['prevision'],
            rol=PerfilUsuario.Rol.PACIENTE,
        )
        return user


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        aplicar_estilos_bootstrap(self)
