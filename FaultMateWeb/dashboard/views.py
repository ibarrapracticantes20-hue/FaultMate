# Este archivo contiene las "vistas" de la app dashboard.
# Una vista es simplemente una funcion de Python que recibe una peticion
# (request) y devuelve una respuesta (normalmente un render con un template HTML).
import unicodedata

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Diagnostico
from agentes.models import Agentes
from faultmate.services.gemini_service import consultar_gemini


BASE_CONOCIMIENTO = {
    'motor no arranca': {
        'diagnostico': 'Verificar alimentacion electrica, fusibles, contactor y proteccion termica. Se detecta fusible abierto.',
        'tiempo': 2,
    },
    'baja presion hidraulica': {
        'diagnostico': 'Revisar nivel de aceite, filtro hidraulico y estado de la bomba. Se detecta filtro obstruido.',
        'tiempo': 3,
    },
    'movimiento lento de motor': {
        'diagnostico': 'Verificar voltaje de alimentacion, sobrecarga mecanica y estado de rodamientos. Se detecta bajo voltaje.',
        'tiempo': 2,
    },
    'movimeinto lento de motor': {
        'diagnostico': 'Verificar voltaje de alimentacion, sobrecarga mecanica y estado de rodamientos. Se detecta bajo voltaje.',
        'tiempo': 2,
    },
    'fuga de aceite': {
        'diagnostico': 'Inspeccionar mangueras, sellos y conexiones hidraulicas. Se detecta sello deteriorado.',
        'tiempo': 2,
    },
    'sobrecalentamiento de motor': {
        'diagnostico': 'Revisar ventilacion, carga aplicada y estado de rodamientos. Se detecta ventilacion insuficiente.',
        'tiempo': 3,
    },
    'vibracion excesiva': {
        'diagnostico': 'Verificar alineacion, balanceo y desgaste de rodamientos. Se detecta desalineacion del eje.',
        'tiempo': 2,
    },
    'banda detenida': {
        'diagnostico': 'Revisar tension de banda, motor y sensores de seguridad. Se detecta banda rota.',
        'tiempo': 2,
    },
    'cilindro no avanza': {
        'diagnostico': 'Verificar presion neumatica, valvulas y actuador. Se detecta valvula atascada.',
        'tiempo': 2,
    },
    'bomba sin presion': {
        'diagnostico': 'Revisar cebado, valvula de alivio y desgaste interno. Se detecta falta de cebado.',
        'tiempo': 2,
    },
    'ruido en motor': {
        'diagnostico': 'Revisar rodamientos, lubricacion y elementos sueltos. Se detecta rodamiento desgastado.',
        'tiempo': 2,
    },
}


def normalizar_texto(texto):
    """Normaliza texto para comparar fallas sin tildes y sin mayusculas."""
    texto = (texto or '').strip().lower()
    texto = unicodedata.normalize('NFKD', texto)
    return ''.join(char for char in texto if not unicodedata.combining(char))


def buscar_en_base_conocimiento(falla):
    """Busca coincidencia de la falla en la base manual de conocimiento."""
    falla_normalizada = normalizar_texto(falla)

    for falla_base, data in BASE_CONOCIMIENTO.items():
        if falla_base in falla_normalizada or falla_normalizada in falla_base:
            return data

    return None


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
    diagnostico_mostrado = None
    buscado = False

    if request.method == 'POST':
        buscado = True
        falla = request.POST.get('falla', '').strip()

        # 0) Si la falla esta en la base manual, NO se consulta Gemini.
        diagnostico_base = buscar_en_base_conocimiento(falla)
        if diagnostico_base is not None:
            diagnostico_mostrado = Diagnostico.objects.create(
                falla=falla,
                diagnostico=diagnostico_base['diagnostico'],
                agente='Base de Conocimiento',
                tiempo_diagnostico=diagnostico_base['tiempo']
            )
            return render(
                request,
                'dashboard/diagnosticar.html',
                {
                    'diagnostico_mostrado': diagnostico_mostrado,
                    'buscado': buscado
                }
            )

        # 1) Buscar si la falla ya fue diagnosticada antes.
        diagnostico_mostrado = Diagnostico.objects.filter(
            falla__icontains=falla
        ).first()

        # 2) Si no existe un diagnostico previo, se consulta a la IA.
        if diagnostico_mostrado is None:
            respuesta_gemini = consultar_gemini(falla)

            diagnostico_mostrado = Diagnostico.objects.create(
                falla=falla,
                diagnostico=respuesta_gemini,
                agente="Gemini IA",
                tiempo_diagnostico=1
            )

    return render(
        request,
        'dashboard/diagnosticar.html',
        {
            'diagnostico_mostrado': diagnostico_mostrado,
            'buscado': buscado
        }
    )


@login_required
def diagnostico_detalle(request, diagnostico_id):
    """Muestra el diagnostico completo en una pagina separada."""
    diagnostico = get_object_or_404(Diagnostico, id=diagnostico_id)
    return render(request, 'dashboard/diagnostico_detalle.html', {'diagnostico': diagnostico})