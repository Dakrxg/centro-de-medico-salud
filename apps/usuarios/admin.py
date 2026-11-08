from django.contrib import admin

from .models import PerfilUsuario


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'rut', 'telefono', 'rol', 'prevision')
    list_filter = ('rol', 'prevision')
    search_fields = ('user__username', 'rut', 'user__email')
    list_select_related = ('user',)
