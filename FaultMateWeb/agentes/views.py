# Vistas de la app "agentes": aqui se administran los "Agentes IA"
# (los perfiles de inteligencia artificial que ayudan a diagnosticar fallas).
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Agentes


@login_required
def lista_agentes(request):
    """Muestra todos los agentes IA guardados en la base de datos."""
    agentes = Agentes.objects.all()

    return render(
        request,
        'agentes/lista_agentes.html',
        {
            'agentes': agentes
        }
    )


@login_required
def nuevo_agente(request):
    """Crea un nuevo agente IA a partir de los datos del formulario."""
    if request.method == 'POST':
        Agentes.objects.create(
            nombre=request.POST.get('nombre'),
            descripcion=request.POST.get('descripcion')
        )

        # Una vez guardado, regresamos a la lista de agentes.
        return redirect('lista_agentes')

    return render(
        request,
        'agentes/nuevo_agente.html'
    )


@login_required
def editar_agente(request, id):
    """Edita los datos de un agente IA que ya existe."""
    agente = get_object_or_404(Agentes, id=id)

    if request.method == 'POST':
        agente.nombre = request.POST.get('nombre')
        agente.descripcion = request.POST.get('descripcion')
        agente.save()

        return redirect('lista_agentes')

    return render(
        request,
        'agentes/editar_agente.html',
        {
            'agente': agente
        }
    )


@login_required
def eliminar_agente(request, id):
    """Elimina un agente IA de la base de datos."""
    agente = get_object_or_404(Agentes, id=id)
    agente.delete()

    # Antes esto redirigia a "/agente/" (sin la "s"), una direccion que
    # no existe y provocaba un error 404. Usamos el nombre de la ruta
    # ("lista_agentes") para evitar ese tipo de errores de escritura.
    return redirect('lista_agentes')