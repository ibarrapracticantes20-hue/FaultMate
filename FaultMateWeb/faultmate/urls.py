# Este es el archivo "principal" de direcciones (URLs) del proyecto.
# Aqui se decide a que app le toca atender cada direccion web.
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),            # Panel de administracion de Django.
    path('', include('dashboard.urls')),         # Paginas generales (inicio, dashboard, etc.)
    path('agentes/', include('agentes.urls')),   # Todo "/agentes/..." (CRUD de agentes IA).
    path('usuarios/', include('usuarios.urls')), # Todo "/usuarios/..." (lista y alta de usuarios).
]
