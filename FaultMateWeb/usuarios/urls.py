# Direcciones (URLs) de la app "usuarios".
# Todas empiezan en "/usuarios/" porque asi se conecto en FaultMateWeb/faultmate/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # /usuarios/  -> ver la lista de usuarios
    path('', views.lista_usuarios, name='usuarios'),

    # /usuarios/nuevo/  -> formulario para crear un usuario nuevo
    path('nuevo/', views.nuevo_usuario, name='nuevo_usuario'),
]
