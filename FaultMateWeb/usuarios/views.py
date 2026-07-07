# Vistas de la app "usuarios": lista de usuarios del sistema y alta de
# nuevos usuarios (que ademas puedan iniciar sesion).
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .models import Usuario


@login_required
def lista_usuarios(request):
    """Muestra todos los usuarios registrados en el sistema."""
    usuarios = Usuario.objects.all()

    return render(
        request,
        'usuarios/lista_usuarios.html',
        {
            'usuarios': usuarios
        }
    )


@login_required
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
    error = None

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        rol = request.POST.get('rol') or 'Tecnico'
        password = request.POST.get('password')

        ya_existe = (
            Usuario.objects.filter(correo=correo).exists()
            or User.objects.filter(username=correo).exists()
        )

        if ya_existe:
            error = 'Ya existe un usuario con ese correo.'
        elif not password:
            # Nunca dejamos crear un usuario sin contrasena: si no hay
            # contrasena, nadie podria iniciar sesion de forma segura.
            error = 'Debes escribir una contrasena.'
        else:
            User.objects.create_user(username=correo, email=correo, password=password)
            Usuario.objects.create(nombre=nombre, correo=correo, rol=rol)

            return redirect('usuarios')

    return render(request, 'usuarios/nuevo_usuario.html', {'error': error})

