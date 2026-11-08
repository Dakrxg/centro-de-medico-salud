from django.conf import settings
from django.contrib import admin

from .models import EspecialidadMedica, PrestacionMedica

# Identidad corporativa del panel de administración
admin.site.site_header = f'{settings.NOMBRE_ORGANIZACION} - Panel de Control'
admin.site.site_title = f'{settings.NOMBRE_ORGANIZACION} Admin'
admin.site.index_title = 'Gestión Operativa de Recursos y Servicios'


@admin.register(EspecialidadMedica)
class EspecialidadMedicaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug', 'icono', 'activa', 'creada_en')
    list_filter = ('activa',)
    search_fields = ('nombre', 'descripcion')
    prepopulated_fields = {'slug': ('nombre',)}
    list_editable = ('activa',)


@admin.register(PrestacionMedica)
class PrestacionMedicaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'especialidad', 'arancel', 'cupos_diarios', 'estado', 'vigente')
    list_display_links = ('codigo', 'nombre')
    list_filter = ('especialidad', 'estado', 'vigente')
    search_fields = ('codigo', 'nombre', 'descripcion')
    list_editable = ('arancel', 'estado', 'vigente')
    list_select_related = ('especialidad',)
    list_per_page = 15
    readonly_fields = ('slug', 'fecha_creacion', 'fecha_actualizacion')
    fieldsets = (
        ('Identificación', {'fields': ('especialidad', 'codigo', 'slug', 'nombre')}),
        ('Descripción clínica', {'fields': ('descripcion', 'requisitos', 'imagen')}),
        ('Valores y capacidad', {'fields': ('arancel', 'duracion_minutos', 'cupos_diarios')}),
        ('Estado operativo', {'fields': ('estado', 'vigente', 'destacada')}),
        ('Auditoría', {'classes': ('collapse',), 'fields': ('fecha_creacion', 'fecha_actualizacion')}),
    )
