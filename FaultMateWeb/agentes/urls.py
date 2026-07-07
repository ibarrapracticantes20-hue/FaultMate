# Direcciones (URLs) de la app "agentes".
# Todas empiezan en "/agentes/" porque asi se conecto en FaultMateWeb/faultmate/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # /agentes/  -> ver la lista de agentes IA
    path('', views.lista_agentes, name='lista_agentes'),

    # /agentes/nuevo/  -> formulario para crear un agente IA
    path('nuevo/', views.nuevo_agente, name='nuevo_agente'),

    # /agentes/editar/5/  -> formulario para editar el agente con id=5
    path('editar/<int:id>/', views.editar_agente, name='editar_agente'),

    # /agentes/eliminar/5/  -> elimina el agente con id=5
    path('eliminar/<int:id>/', views.eliminar_agente, name='eliminar_agente'),
]