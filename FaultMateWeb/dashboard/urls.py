# Aqui se definen las direcciones (URLs) que maneja la app "dashboard".
# Cada "path" conecta una direccion web con una funcion de views.py.
#
# Importante: ni "/agentes/" ni "/usuarios/" se definen aqui porque ya
# pertenecen por completo a sus propias apps (ver FaultMateWeb/faultmate/urls.py,
# FaultMateWeb/agentes/urls.py y FaultMateWeb/usuarios/urls.py). Antes
# "/usuarios/" tambien vivia aqui Y en la app "usuarios" al mismo tiempo,
# lo mismo que paso con "/agentes/": dos vistas compitiendo por la misma
# direccion, y una de las dos quedaba inutilizable.
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('diagnosticos/', views.diagnosticos, name='diagnosticos'),
    path('diagnosticar/', views.diagnosticar, name='diagnosticar'),
    path('diagnosticos/<int:diagnostico_id>/', views.diagnostico_detalle, name='diagnostico_detalle'),
    path('diagnosticos/<int:diagnostico_id>/eliminar/', views.eliminar_diagnostico, name='eliminar_diagnostico'),
]
