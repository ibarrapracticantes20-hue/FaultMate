# Vistas de la app "usuarios": lista de usuarios del sistema y alta de
# nuevos usuarios (que ademas puedan iniciar sesion).
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect

from faultmate.permissions import ROLE_DESARROLLADOR, role_required
from .forms import UsuarioForm
from .models import Usuario


@login_required
@role_required(ROLE_DESARROLLADOR)
def lista_usuarios(request):
    """Muestra todos los usuarios registrados en el sistema."""
    usuarios = Usuario.objects.all().order_by('id')

    return render(
        request,
        'usuarios/lista_usuarios.html',
        {
            'usuarios': usuarios
        }
    )


@login_required
@role_required(ROLE_DESARROLLADOR)
def nuevo_usuario(request):
    """
    Crea un nuevo usuario.

    Aqui se crean DOS cosas a la vez:
    1. Un "Usuario" (nuestro modelo) para mostrarlo en la tabla con su
       nombre, correo y rol.
    2. Un "User" de Django (auth.User) para que esa persona pueda
       iniciar sesion con su correo y contrasena.

    Usamos el correo como nombre de usuario para iniciar sesion, asi
    no hay que inventar un "usuario" aparte.
    """
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data['correo']
            password = form.cleaned_data.get('password')

            if not password:
                form.add_error('password', 'Debes escribir una contrasena.')
            elif User.objects.filter(username=correo).exists():
                form.add_error('correo', 'Ya existe un usuario con ese correo.')
            else:
                rol = form.cleaned_data['rol']
                auth_user = User.objects.create_user(
                    username=correo,
                    email=correo,
                    password=password,
                )
                auth_user.is_staff = rol in [Usuario.ROLE_ADMIN, Usuario.ROLE_DESARROLLADOR]
                auth_user.is_superuser = rol == Usuario.ROLE_DESARROLLADOR
                auth_user.save()

                usuario = form.save(commit=False)
                usuario.auth_user = auth_user
                usuario.save()
                return redirect('usuarios')
    else:
        form = UsuarioForm(initial={'rol': Usuario.ROLE_VISITANTE})

    return render(request, 'usuarios/nuevo_usuario.html', {'form': form})


@login_required
@role_required(ROLE_DESARROLLADOR)
def editar_usuario(request, id):
    """Edita usuario de FaultMate y sincroniza datos de auth.User."""
    usuario = get_object_or_404(Usuario, id=id)

    if request.method == 'POST':
        correo_anterior = usuario.correo
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            correo_nuevo = form.cleaned_data['correo']

            auth_user = usuario.auth_user or User.objects.filter(username=correo_anterior).first()

            if auth_user and correo_nuevo != auth_user.username and User.objects.filter(username=correo_nuevo).exists():
                form.add_error('correo', 'Ya existe un usuario con ese correo.')
            else:
                usuario_actualizado = form.save(commit=False)
                rol = form.cleaned_data['rol']
                if auth_user:
                    auth_user.username = correo_nuevo
                    auth_user.email = correo_nuevo
                    auth_user.is_staff = rol in [Usuario.ROLE_ADMIN, Usuario.ROLE_DESARROLLADOR]
                    auth_user.is_superuser = rol == Usuario.ROLE_DESARROLLADOR
                    auth_user.save()
                    usuario_actualizado.auth_user = auth_user
                usuario_actualizado.save()
                return redirect('usuarios')
    else:
        form = UsuarioForm(instance=usuario)

    return render(request, 'usuarios/editar_usuario.html', {'form': form, 'usuario': usuario})


@login_required
@role_required(ROLE_DESARROLLADOR)
def eliminar_usuario(request, id):
    """Elimina usuario de FaultMate y su cuenta de login asociada."""
    usuario = get_object_or_404(Usuario, id=id)

    if request.method == 'POST':
        auth_user = usuario.auth_user or User.objects.filter(username=usuario.correo).first()
        usuario.delete()
        if auth_user:
            auth_user.delete()
            return redirect('usuarios')

    return redirect('usuarios')

