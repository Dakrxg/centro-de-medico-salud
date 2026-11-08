from django.urls import path

from . import views

app_name = 'catalogo'

urlpatterns = [
    path('', views.prestacion_lista, name='lista'),
    path('prestacion/<slug:slug>/', views.prestacion_detalle, name='detalle'),
    path('gestion/', views.gestion_prestaciones, name='gestion'),
    path('gestion/nueva/', views.prestacion_crear, name='crear'),
    path('gestion/editar/<slug:slug>/', views.prestacion_editar, name='editar'),
    path('gestion/eliminar/<slug:slug>/', views.prestacion_eliminar, name='eliminar'),
    path('gestion/reactivar/<slug:slug>/', views.prestacion_reactivar, name='reactivar'),
]
