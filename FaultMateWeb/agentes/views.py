from django.shortcuts import render, get_object_or_404, redirect
from .models import Agentes

def eliminar_agente(request, id):

    agente = get_object_or_404(Agentes, id=id)

    agente.delete()

    return redirect('/agente/')


def lista_agentes(request):

    agentes = Agentes.objects.all()

    return render(
        request,
        'agentes/lista_agentes.html',
        {
            'agentes': agentes
        }
    )


def editar_agente(request, id):

    agente = get_object_or_404(Agentes, id=id)

    if request.method == 'POST':
        
        agente.nombre = request.POST.get('nombre')
        agente.descripcion = request.POST.get('descripcion')

        agente.save()

        return redirect('/agentes/')
    
    return render(
        request,
        'agentes/editar_agente.html',
        {
            'agente': agente
        }
    )

def nuevo_agente(request):

    if request.method == 'POST':

        Agentes.objects.create(
            nombre=request.POST.get('nombre'),
            descripcion=request.POST.get('descripcion')
        )
        
        return redirect('/agentes/')
    
    return render(
        request,
        'agentes/nuevo_agente.html'
    )