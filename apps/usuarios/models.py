from django.conf import settings
from django.db import models

from .validators import validar_rut


class PerfilUsuario(models.Model):
    """Datos complementarios del usuario: RUT, teléfono, rol institucional y previsión."""

    class Rol(models.TextChoices):
        PACIENTE = 'PACIENTE', 'Paciente'
        ADMINISTRATIVO = 'ADMINISTRATIVO', 'Personal administrativo'
        MEDICO = 'MEDICO', 'Profesional de la salud'

    class Prevision(models.TextChoices):
        FONASA = 'FONASA', 'Fonasa'
        ISAPRE = 'ISAPRE', 'Isapre'
        PARTICULAR = 'PARTICULAR', 'Particular (sin previsión)'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='perfil')
    rut = models.CharField('RUT', max_length=12, unique=True, validators=[validar_rut])
    telefono = models.CharField('teléfono', max_length=20, blank=True)
    rol = models.CharField('rol institucional', max_length=15, choices=Rol.choices, default=Rol.PACIENTE)
    prevision = models.CharField(
        'previsión', max_length=12, choices=Prevision.choices, default=Prevision.PARTICULAR)

    class Meta:
        verbose_name = 'perfil de usuario'
        verbose_name_plural = 'perfiles de usuario'

    def __str__(self):
        return f'{self.user.get_username()} ({self.rut})'
