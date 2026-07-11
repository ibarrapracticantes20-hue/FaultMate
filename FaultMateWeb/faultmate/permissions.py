from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from usuarios.models import Usuario


ROLE_VISITANTE = 'VISITANTE'
ROLE_ADMIN = 'ADMIN'
ROLE_DESARROLLADOR = 'DESARROLLADOR'


def get_usuario_perfil(user):
    if not user.is_authenticated:
        return None

    perfil = Usuario.objects.filter(auth_user=user).first()
    if perfil:
        return perfil

    # Compatibilidad con datos previos donde auth_user podia venir vacio.
    return Usuario.objects.filter(correo=user.username).first()


def get_user_role(user):
    if not user.is_authenticated:
        return None

    if user.is_superuser:
        return ROLE_DESARROLLADOR

    perfil = get_usuario_perfil(user)
    if perfil:
        return perfil.rol

    return ROLE_VISITANTE


def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            role = get_user_role(request.user)
            if role in allowed_roles:
                return view_func(request, *args, **kwargs)

            messages.error(request, 'No tienes permisos para esta accion.')
            return redirect('dashboard')

        return _wrapped

    return decorator
