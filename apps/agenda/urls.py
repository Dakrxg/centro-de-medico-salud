from django.urls import path

from . import views

app_name = 'agenda'

urlpatterns = [
    path('canasta/', views.canasta_ver, name='ver'),
    path('canasta/agregar/<int:pk>/', views.canasta_agregar, name='agregar'),
    path('canasta/actualizar/<int:pk>/', views.canasta_actualizar, name='actualizar'),
    path('canasta/quitar/<int:pk>/', views.canasta_quitar, name='quitar'),
    path('canasta/vaciar/', views.canasta_vaciar, name='vaciar'),
    path('canasta/prevision/', views.canasta_prevision, name='prevision'),
    path('confirmar/', views.checkout_simulado, name='checkout'),
]
