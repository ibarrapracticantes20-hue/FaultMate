# Vistas de la app "agentes": aqui se administran los "Agentes IA"
# (los perfiles de inteligencia artificial que ayudan a diagnosticar fallas).
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect

from faultmate.permissions import ROLE_ADMIN, ROLE_DESARROLLADOR, get_user_role, role_required
from .forms import AgenteForm, GenerarAgenteForm
from .models import Agentes, AgenteChatMensaje, AgenteEvento
from faultmate.services.gemini_service import consultar_gemini_agente


def construir_agente_por_reglas(nombre, dominio, tipo_maquina, nivel_detalle, estilo):
    """Genera configuracion base del agente a partir de reglas simples."""
    temperaturas = {
        'basico': 0.2,
        'intermedio': 0.5,
        'avanzado': 0.7,
    }
    tokens = {
        'basico': 500,
        'intermedio': 900,
        'avanzado': 1300,
    }

    descripcion = (
        f'Agente especializado en {dominio} para {tipo_maquina}. '
        f'Entrega diagnosticos en nivel {nivel_detalle} con estilo {estilo}.'
    )

    prompt = (
        f'Eres {nombre}, un experto en {dominio}. '\
        f'Te enfocas en {tipo_maquina}. '\
        f'Tu nivel de detalle debe ser {nivel_detalle} y tu estilo de comunicacion {estilo}. '\
        'Responde siempre con: Diagnostico probable, Causa raiz, Accion recomendada, Riesgo y Tiempo estimado.'
    )

    return {
        'descripcion': descripcion,
        'prompt': prompt,
        'temperatura': temperaturas[nivel_detalle],
        'tokens': tokens[nivel_detalle],
    }


AGENTES_BASE = [
    {
        'nombre': 'Agente Motores',
        'dominio': 'mantenimiento industrial',
        'tipo_maquina': 'motores electricos',
        'nivel_detalle': 'intermedio',
        'estilo': 'tecnico',
    },
    {
        'nombre': 'Agente Hidraulica',
        'dominio': 'sistemas hidraulicos',
        'tipo_maquina': 'bombas y actuadores',
        'nivel_detalle': 'intermedio',
        'estilo': 'practico',
    },
    {
        'nombre': 'Agente Neumatica',
        'dominio': 'sistemas neumaticos',
        'tipo_maquina': 'cilindros y valvulas',
        'nivel_detalle': 'basico',
        'estilo': 'didactico',
    },
    {
        'nombre': 'Agente Bandas',
        'dominio': 'lineas transportadoras',
        'tipo_maquina': 'bandas y motores de arrastre',
        'nivel_detalle': 'intermedio',
        'estilo': 'practico',
    },
    {
        'nombre': 'Agente Vibraciones',
        'dominio': 'analisis de vibracion',
        'tipo_maquina': 'rodamientos y ejes',
        'nivel_detalle': 'avanzado',
        'estilo': 'tecnico',
    },
]


@login_required
def lista_agentes(request):
    """Muestra todos los agentes IA guardados en la base de datos."""
    agentes_base = Agentes.objects.filter(es_base=True).order_by('id')
    agentes_personalizados = Agentes.objects.filter(es_base=False).order_by('id')

    return render(
        request,
        'agentes/lista_agentes.html',
        {
            'agentes_base': agentes_base,
            'agentes_personalizados': agentes_personalizados,
            'can_manage_agentes': get_user_role(request.user) in [ROLE_ADMIN, ROLE_DESARROLLADOR],
        }
    )


@login_required
@role_required(ROLE_ADMIN, ROLE_DESARROLLADOR)
def nuevo_agente(request):
    """Crea un nuevo agente IA a partir de los datos del formulario."""
    if request.method == 'POST':
        form = AgenteForm(request.POST)
        if form.is_valid():
            agente = form.save(commit=False)
            agente.es_base = False
            agente.save()
            AgenteEvento.objects.create(
                agente=agente,
                usuario=request.user,
                accion='created_manual',
                agente_nombre=agente.nombre,
                agente_es_base=agente.es_base,
            )

            # Una vez guardado, regresamos a la lista de agentes.
            return redirect('lista_agentes')
    else:
        form = AgenteForm(initial={'temperatura': 0.7, 'tokens': 1000})

    return render(request, 'agentes/nuevo_agente.html', {'form': form})


@login_required
@role_required(ROLE_ADMIN, ROLE_DESARROLLADOR)
def editar_agente(request, id):
    """Edita los datos de un agente IA que ya existe."""
    agente = get_object_or_404(Agentes, id=id)

    if request.method == 'POST':
        form = AgenteForm(request.POST, instance=agente)
        if form.is_valid():
            agente = form.save()
            AgenteEvento.objects.create(
                agente=agente,
                usuario=request.user,
                accion='edited',
                agente_nombre=agente.nombre,
                agente_es_base=agente.es_base,
            )
            return redirect('lista_agentes')
    else:
        form = AgenteForm(instance=agente)

    return render(request, 'agentes/editar_agente.html', {'agente': agente, 'form': form})


@login_required
@role_required(ROLE_ADMIN, ROLE_DESARROLLADOR)
def eliminar_agente(request, id):
    """Elimina un agente IA de la base de datos."""
    agente = get_object_or_404(Agentes, id=id)
    if request.method == 'POST':
        AgenteEvento.objects.create(
            agente=None,
            usuario=request.user,
            accion='deleted',
            agente_nombre=agente.nombre,
            agente_es_base=agente.es_base,
        )
        agente.delete()

    # Antes esto redirigia a "/agente/" (sin la "s"), una direccion que
    # no existe y provocaba un error 404. Usamos el nombre de la ruta
    # ("lista_agentes") para evitar ese tipo de errores de escritura.
    return redirect('lista_agentes')


@login_required
@role_required(ROLE_ADMIN, ROLE_DESARROLLADOR)
def generar_agente(request):
    """Genera un agente automaticamente a partir de parametros de negocio."""
    if request.method == 'POST':
        form = GenerarAgenteForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            config = construir_agente_por_reglas(
                data['nombre'],
                data['dominio'],
                data['tipo_maquina'],
                data['nivel_detalle'],
                data['estilo'],
            )
            agente = Agentes.objects.create(
                es_base=False,
                nombre=data['nombre'],
                descripcion=config['descripcion'],
                prompt=config['prompt'],
                temperatura=config['temperatura'],
                tokens=config['tokens'],
            )
            AgenteEvento.objects.create(
                agente=agente,
                usuario=request.user,
                accion='created_generated',
                agente_nombre=agente.nombre,
                agente_es_base=agente.es_base,
            )
            return redirect('lista_agentes')
    else:
        form = GenerarAgenteForm()

    return render(request, 'agentes/generar_agente.html', {'form': form})


@login_required
@role_required(ROLE_ADMIN, ROLE_DESARROLLADOR)
def generar_agentes_base(request):
    """Crea un conjunto inicial de agentes base sin duplicarlos por nombre."""
    if request.method == 'POST':
        for agente_base in AGENTES_BASE:
            if Agentes.objects.filter(nombre=agente_base['nombre']).exists():
                continue

            config = construir_agente_por_reglas(
                agente_base['nombre'],
                agente_base['dominio'],
                agente_base['tipo_maquina'],
                agente_base['nivel_detalle'],
                agente_base['estilo'],
            )
            Agentes.objects.create(
                es_base=True,
                nombre=agente_base['nombre'],
                descripcion=config['descripcion'],
                prompt=config['prompt'],
                temperatura=config['temperatura'],
                tokens=config['tokens'],
            )
            agente = Agentes.objects.get(nombre=agente_base['nombre'])
            AgenteEvento.objects.create(
                agente=agente,
                usuario=request.user,
                accion='created_base',
                agente_nombre=agente.nombre,
                agente_es_base=True,
            )

    return redirect('lista_agentes')


@login_required
def chat_agente(request, id):
    """Chat especializado por agente con historial persistente por usuario."""
    agente = get_object_or_404(Agentes, id=id)

    if request.method == 'POST':
        mensaje_usuario = (request.POST.get('mensaje') or '').strip()
        if mensaje_usuario:
            AgenteChatMensaje.objects.create(
                agente=agente,
                usuario=request.user,
                rol='user',
                contenido=mensaje_usuario,
            )

            historial = list(
                AgenteChatMensaje.objects.filter(agente=agente, usuario=request.user)
                .values('rol', 'contenido')
            )
            respuesta = consultar_gemini_agente(agente, mensaje_usuario, historial)

            AgenteChatMensaje.objects.create(
                agente=agente,
                usuario=request.user,
                rol='assistant',
                contenido=respuesta,
            )
            AgenteEvento.objects.create(
                agente=agente,
                usuario=request.user,
                accion='chat_used',
                agente_nombre=agente.nombre,
                agente_es_base=agente.es_base,
            )

        # PRG: evita reenvio al recargar o volver atras.
        return redirect('chat_agente', id=agente.id)

    mensajes = AgenteChatMensaje.objects.filter(agente=agente, usuario=request.user)

    return render(
        request,
        'agentes/chat_agente.html',
        {
            'agente': agente,
            'mensajes': mensajes,
        },
    )


@login_required
def limpiar_chat_agente(request, id):
    """Limpia historial del chat del agente para el usuario actual."""
    agente = get_object_or_404(Agentes, id=id)
    if request.method == 'POST':
        AgenteChatMensaje.objects.filter(agente=agente, usuario=request.user).delete()
        messages.success(request, 'Se limpio el historial de chat del agente.')
    return redirect('chat_agente', id=agente.id)