# Direcciones (URLs) de la app "usuarios".
# Todas empiezan en "/usuarios/" porque asi se conecto en FaultMateWeb/faultmate/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # /usuarios/  -> ver la lista de usuarios
    path('', views.lista_usuarios, name='usuarios'),

    # /usuarios/nuevo/  -> formulario para crear un usuario nuevo
    path('nuevo/', views.nuevo_usuario, name='nuevo_usuario'),

    # /usuarios/editar/5/  -> editar usuario existente
    path('editar/<int:id>/', views.editar_usuario, name='editar_usuario'),

    # /usuarios/eliminar/5/  -> eliminar usuario existente
    path('eliminar/<int:id>/', views.eliminar_usuario, name='eliminar_usuario'),
]
