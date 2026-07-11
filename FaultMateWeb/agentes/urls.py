# Direcciones (URLs) de la app "agentes".
# Todas empiezan en "/agentes/" porque asi se conecto en FaultMateWeb/faultmate/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # /agentes/  -> ver la lista de agentes IA
    path('', views.lista_agentes, name='lista_agentes'),

    # /agentes/nuevo/  -> formulario para crear un agente IA
    path('nuevo/', views.nuevo_agente, name='nuevo_agente'),

    # /agentes/generar/ -> formulario para generar un agente automaticamente
    path('generar/', views.generar_agente, name='generar_agente'),

    # /agentes/generar-base/ -> crea un conjunto de agentes base
    path('generar-base/', views.generar_agentes_base, name='generar_agentes_base'),

    # /agentes/editar/5/  -> formulario para editar el agente con id=5
    path('editar/<int:id>/', views.editar_agente, name='editar_agente'),

    # /agentes/chat/5/ -> chat especializado por agente
    path('chat/<int:id>/', views.chat_agente, name='chat_agente'),

    # /agentes/chat/5/limpiar/ -> limpia historial del chat del agente
    path('chat/<int:id>/limpiar/', views.limpiar_chat_agente, name='limpiar_chat_agente'),

    # /agentes/eliminar/5/  -> elimina el agente con id=5
    path('eliminar/<int:id>/', views.eliminar_agente, name='eliminar_agente'),
]