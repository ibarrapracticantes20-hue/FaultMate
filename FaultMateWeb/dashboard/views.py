# Este archivo contiene las "vistas" de la app dashboard.
# Una vista es simplemente una funcion de Python que recibe una peticion
# (request) y devuelve una respuesta (normalmente un render con un template HTML).
import unicodedata
from datetime import datetime
from io import BytesIO

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from openpyxl import Workbook
from .models import Diagnostico
from agentes.models import Agentes, AgenteChatMensaje, AgenteEvento
from faultmate.permissions import ROLE_DESARROLLADOR, get_user_role
from usuarios.models import Usuario
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
    'falla en sensor inductivo': {
        'diagnostico': 'Verificar distancia de sensado, cableado y voltaje de alimentacion. Se detecta desajuste de posicion.',
        'tiempo': 2,
    },
    'variador marca sobrecorriente': {
        'diagnostico': 'Revisar parametros de rampa, carga mecanica y aislamiento del motor. Se detecta aceleracion demasiado corta.',
        'tiempo': 3,
    },
    'compresor no enciende': {
        'diagnostico': 'Revisar proteccion termica, presostato y contactor. Se detecta presostato defectuoso.',
        'tiempo': 3,
    },
    'presion neumatica inestable': {
        'diagnostico': 'Inspeccionar regulador, fugas y drenado de humedad. Se detecta regulador descalibrado.',
        'tiempo': 2,
    },
    'falla de comunicacion plc': {
        'diagnostico': 'Verificar red industrial, direccionamiento IP y estado de switch. Se detecta conflicto de IP.',
        'tiempo': 3,
    },
    'paro por temperatura alta en horno': {
        'diagnostico': 'Revisar termopar, controlador PID y ventilacion. Se detecta termopar fuera de rango.',
        'tiempo': 3,
    },
    'cinta transportadora desalineada': {
        'diagnostico': 'Ajustar rodillos guia, tension y centrado de banda. Se detecta desbalance en rodillo lateral.',
        'tiempo': 2,
    },
    'robot fuera de trayectoria': {
        'diagnostico': 'Revisar calibracion, referencias de cero y holguras mecanicas. Se detecta perdida de calibracion.',
        'tiempo': 4,
    },
    'consumo electrico elevado en bomba': {
        'diagnostico': 'Verificar cavitacion, obstrucciones y estado de impulsor. Se detecta obstruccion parcial en succion.',
        'tiempo': 3,
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

    Si la persona YA inicio sesion, mostramos una bienvenida privada con
    datos rapidos y actividad reciente. Si no ha iniciado sesion, mostramos
    la pantalla publica con boton de acceso.
    """
    if request.user.is_authenticated:
        total_diagnosticos = Diagnostico.objects.count()
        total_agentes = Agentes.objects.count()
        total_usuarios = Usuario.objects.count()
        total_preguntas = AgenteChatMensaje.objects.filter(rol='user').count()

        conversaciones_usuario = (
            AgenteChatMensaje.objects
            .filter(usuario=request.user, rol='user')
            .values('agente_id')
            .distinct()
            .count()
        )

        recientes_diagnosticos = Diagnostico.objects.order_by('-fecha')[:5]

        diagnosticos_data = []
        for item in Diagnostico.objects.order_by('-fecha'):
            diagnosticos_data.append(
                {
                    'id': item.id,
                    'falla': item.falla,
                    'agente': item.agente,
                    'fecha_dia': item.fecha.strftime('%Y-%m-%d'),
                    'tiempo_diagnostico': item.tiempo_diagnostico,
                }
            )

        ultimos_bots = (
            AgenteChatMensaje.objects
            .filter(usuario=request.user, rol='assistant')
            .values('agente__nombre')
            .annotate(usos=Count('id'))
            .order_by('-usos')[:5]
        )

        return render(
            request,
            'dashboard/inicio.html',
            {
                'total_diagnosticos': total_diagnosticos,
                'total_agentes': total_agentes,
                'total_usuarios': total_usuarios,
                'total_preguntas': total_preguntas,
                'conversaciones_usuario': conversaciones_usuario,
                'recientes_diagnosticos': recientes_diagnosticos,
                'ultimos_bots': ultimos_bots,
                'inicio_chart_raw_diagnosticos': diagnosticos_data,
                'can_create_users': get_user_role(request.user) == ROLE_DESARROLLADOR,
            },
        )

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
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    rol = request.GET.get('rol')

    diagnosticos_qs = Diagnostico.objects.all()
    chats_qs = AgenteChatMensaje.objects.all()
    eventos_qs = AgenteEvento.objects.all()

    if fecha_inicio:
        try:
            datetime.strptime(fecha_inicio, '%Y-%m-%d')
            diagnosticos_qs = diagnosticos_qs.filter(fecha__date__gte=fecha_inicio)
            chats_qs = chats_qs.filter(creado_en__date__gte=fecha_inicio)
            eventos_qs = eventos_qs.filter(creado_en__date__gte=fecha_inicio)
        except ValueError:
            fecha_inicio = ''

    if fecha_fin:
        try:
            datetime.strptime(fecha_fin, '%Y-%m-%d')
            diagnosticos_qs = diagnosticos_qs.filter(fecha__date__lte=fecha_fin)
            chats_qs = chats_qs.filter(creado_en__date__lte=fecha_fin)
            eventos_qs = eventos_qs.filter(creado_en__date__lte=fecha_fin)
        except ValueError:
            fecha_fin = ''

    roles_validos = {x[0] for x in Usuario.ROLE_CHOICES}
    if rol:
        if rol in roles_validos:
            usuarios_ids = list(
                Usuario.objects.filter(rol=rol, auth_user__isnull=False)
                .values_list('auth_user_id', flat=True)
            )
            diagnosticos_qs = diagnosticos_qs.filter(usuario_id__in=usuarios_ids)
            chats_qs = chats_qs.filter(usuario_id__in=usuarios_ids)
            eventos_qs = eventos_qs.filter(usuario_id__in=usuarios_ids)
        else:
            rol = ''

    if request.GET.get('export') == 'excel':
        wb = Workbook()
        ws = wb.active
        ws.title = 'Diagnosticos'
        ws.append(['Fecha', 'Falla', 'Diagnostico', 'Agente', 'Tiempo (min)', 'Usuario'])

        for d in diagnosticos_qs.select_related('usuario').order_by('-fecha'):
            ws.append([
                d.fecha.strftime('%Y-%m-%d %H:%M:%S'),
                d.falla,
                d.diagnostico,
                d.agente,
                d.tiempo_diagnostico,
                d.usuario.username if d.usuario else '',
            ])

        output = BytesIO()
        wb.save(output)
        output.seek(0)

        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename="faultmate_reporte.xlsx"'
        return response

    total_diagnosticos = diagnosticos_qs.count()
    total_agentes = Agentes.objects.count()
    total_usuarios = Usuario.objects.count()
    total_mensajes = chats_qs.count()
    total_preguntas = chats_qs.filter(rol='user').count()

    conversaciones = (
        chats_qs
        .values('agente_id', 'usuario_id')
        .distinct()
        .count()
    )

    agentes_diferentes_usados = (
        eventos_qs
        .filter(accion='chat_used')
        .values('agente_id')
        .distinct()
        .count()
    )

    agentes_base_usados = (
        eventos_qs
        .filter(accion='chat_used', agente_es_base=True)
        .values('agente_nombre')
        .distinct()
        .count()
    )

    agentes_eliminados = eventos_qs.filter(accion='deleted').count()

    usuarios_activos_chat = (
        chats_qs
        .filter(rol='user')
        .values('usuario_id')
        .distinct()
        .count()
    )

    usabilidad = round((usuarios_activos_chat / total_usuarios) * 100, 1) if total_usuarios else 0

    diagnosticos = diagnosticos_qs.order_by('-fecha')[:10]

    # Datos crudos para construir gráficas interactivas con filtros cruzados en frontend.
    diagnosticos_data = []
    for item in diagnosticos_qs.order_by('-fecha'):
        diagnosticos_data.append(
            {
                'id': item.id,
                'falla': item.falla,
                'agente': item.agente,
                'fecha_dia': item.fecha.strftime('%Y-%m-%d'),
                'tiempo_diagnostico': item.tiempo_diagnostico,
            }
        )

    # Métricas auxiliares para conservar contexto del módulo de agentes.
    chats_por_agente_qs = (
        chats_qs
        .filter(rol='user')
        .values('agente__nombre')
        .annotate(total=Count('id'))
        .order_by('-total')[:8]
    )
    chart_bar_labels = [x['agente__nombre'] for x in chats_por_agente_qs]
    chart_bar_values = [x['total'] for x in chats_por_agente_qs]

    eventos_resumen = eventos_qs.values('accion').annotate(total=Count('id')).order_by('accion')
    eventos_labels = [x['accion'] for x in eventos_resumen]
    eventos_values = [x['total'] for x in eventos_resumen]

    roles_filtro = Usuario.ROLE_CHOICES

    context = {
        'total_diagnosticos': total_diagnosticos,
        'total_agentes': total_agentes,
        'total_usuarios': total_usuarios,
        'total_mensajes': total_mensajes,
        'total_preguntas': total_preguntas,
        'conversaciones': conversaciones,
        'agentes_diferentes_usados': agentes_diferentes_usados,
        'agentes_base_usados': agentes_base_usados,
        'agentes_eliminados': agentes_eliminados,
        'usabilidad': usabilidad,
        'diagnosticos': diagnosticos,
        'chart_raw_diagnosticos': diagnosticos_data,
        'chart_bar_labels': chart_bar_labels,
        'chart_bar_values': chart_bar_values,
        'eventos_labels': eventos_labels,
        'eventos_values': eventos_values,
        'roles_filtro': roles_filtro,
        'filtro_fecha_inicio': fecha_inicio or '',
        'filtro_fecha_fin': fecha_fin or '',
        'filtro_rol': rol or '',
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

    Registra SIEMPRE un nuevo diagnóstico en historial con fecha y hora.
    """
    diagnostico_mostrado = None
    buscado = False

    if request.method == 'POST':
        buscado = True
        falla = request.POST.get('falla', '').strip()
        texto_diagnostico = ''
        agente_origen = 'Gemini IA'
        tiempo_estimado = 1

        # 0) Si la falla esta en la base manual, NO se consulta Gemini.
        diagnostico_base = buscar_en_base_conocimiento(falla)
        if diagnostico_base is not None:
            texto_diagnostico = diagnostico_base['diagnostico']
            agente_origen = 'Base de Conocimiento'
            tiempo_estimado = diagnostico_base['tiempo']
        else:
            # Si no esta en base, intenta reutilizar ultimo diagnostico similar.
            previo = Diagnostico.objects.filter(
                falla__icontains=falla
            ).order_by('-fecha').first()

            if previo is not None:
                texto_diagnostico = previo.diagnostico
                agente_origen = previo.agente
                tiempo_estimado = previo.tiempo_diagnostico
            else:
                texto_diagnostico = consultar_gemini(falla)

        diagnostico_mostrado = Diagnostico.objects.create(
            falla=falla,
            diagnostico=texto_diagnostico,
            agente=agente_origen,
            tiempo_diagnostico=tiempo_estimado,
            usuario=request.user,
        )

    historial_diagnosticos = Diagnostico.objects.filter(usuario=request.user).order_by('-fecha')[:20]

    return render(
        request,
        'dashboard/diagnosticar.html',
        {
            'diagnostico_mostrado': diagnostico_mostrado,
            'buscado': buscado,
            'historial_diagnosticos': historial_diagnosticos,
        }
    )


@login_required
def diagnostico_detalle(request, diagnostico_id):
    """Muestra el diagnostico completo en una pagina separada."""
    diagnostico = get_object_or_404(Diagnostico, id=diagnostico_id)
    return render(request, 'dashboard/diagnostico_detalle.html', {'diagnostico': diagnostico})


@login_required
def eliminar_diagnostico(request, diagnostico_id):
    """Elimina un diagnóstico del historial del usuario actual."""
    diagnostico = get_object_or_404(Diagnostico, id=diagnostico_id, usuario=request.user)
    if request.method == 'POST':
        diagnostico.delete()
    return redirect('diagnosticar')