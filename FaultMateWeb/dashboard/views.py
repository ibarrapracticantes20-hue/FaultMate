# Este archivo contiene las "vistas" de la app dashboard.
# Una vista es simplemente una funcion de Python que recibe una peticion
# (request) y devuelve una respuesta (normalmente un render con un template HTML).
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Diagnostico
from agentes.models import Agentes
from faultmate.services.gemini_service import consultar_gemini


def home(request):
    """
    Pagina de inicio publica (antes de entrar al sistema).

    Si la persona YA inicio sesion, no tiene sentido mostrarle otra vez
    la pantalla de bienvenida (antes esto pasaba y se veia como si el
    "inicio" repitiera todo el menu de nuevo). En ese caso la mandamos
    directo al dashboard.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    return render(request, 'dashboard/index.html')


def login_view(request):
    """
    Muestra el formulario de inicio de sesion y valida usuario/contrasena.

    Antes este formulario no validaba nada: cualquier clic en "Ingresar"
    (incluso sin escribir contrasena) te dejaba entrar. Ahora usamos el
    sistema de autenticacion de Django (authenticate + login), que solo
    deja pasar si el usuario y la contrasena son correctos.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    error = None

    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        password = request.POST.get('password')

        # authenticate() regresa None si el usuario no existe, si la
        # contrasena esta mal, o si viene vacia. Asi evitamos que
        # alguien entre sin una contrasena valida.
        user = authenticate(request, username=usuario, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')

        error = 'Usuario o contrasena incorrectos.'

    return render(request, 'dashboard/registration/login.html', {'error': error})


def logout_view(request):
    """Cierra la sesion del usuario actual y regresa a la pagina de inicio."""
    if request.method == 'POST':
        logout(request)

    return redirect('home')


@login_required
def dashboard(request):
    """Pantalla principal con un resumen (numero de diagnosticos, agentes, etc.)."""
    total_diagnosticos = Diagnostico.objects.count()
    total_agentes = Agentes.objects.count()
    diagnosticos = Diagnostico.objects.all()

    context = {
        'total_diagnosticos': total_diagnosticos,
        'total_agentes': total_agentes,
        'diagnosticos': diagnosticos
    }

    return render(request, 'dashboard/dashboard.html', context)


@login_required
def diagnosticos(request):
    """Muestra el historial de diagnosticos guardados en la base de datos."""
    diagnosticos = Diagnostico.objects.all().order_by('-fecha')

    return render(
        request,
        'dashboard/diagnosticos.html',
        {
            'diagnosticos': diagnosticos
        }
    )


@login_required
def diagnosticar(request):
    """
    Vista principal de diagnostico de fallas.

    Logica simple:
    1. El tecnico escribe la descripcion de una falla.
    2. Primero buscamos si esa falla ya existe en la base de datos.
    3. Si no existe, le preguntamos a la IA (Gemini) y guardamos su respuesta
       para no tener que volver a preguntarle la proxima vez.
    """
    resultado = None
    respuesta_gemini = None
    buscado = False

    if request.method == 'POST':
        buscado = True
        falla = request.POST.get('falla')

        # 1) Buscar si la falla ya fue diagnosticada antes.
        resultado = Diagnostico.objects.filter(
            falla__icontains=falla
        ).first()

        # 2) Si no existe un diagnostico previo, se consulta a la IA.
        if resultado is None:
            respuesta_gemini = consultar_gemini(falla)

            Diagnostico.objects.create(
                falla=falla,
                diagnostico=respuesta_gemini,
                agente="Gemini IA",
                tiempo_diagnostico=1
            )

    return render(
        request,
        'dashboard/diagnosticar.html',
        {
            'resultado': resultado,
            'respuesta_gemini': respuesta_gemini,
            'buscado': buscado
        }
    )