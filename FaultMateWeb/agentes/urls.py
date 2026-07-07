from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_agentes, name='lista_agentes'),

    path(
        'nuevo/',
        views.nuevo_agente,
        name='nuevo_agente'
    ),

    path(
        'editar/<int:id>/',
         views.editar_agente, 
         name='editar_agente'
    ),

    path(
        'eliminar/<int:id>/',
         views.eliminar_agente, 
         name='eliminar_agente'
    ),
] 