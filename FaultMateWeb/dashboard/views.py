from usuarios.models import Usuario
from django.shortcuts import render
from .models import Diagnostico 
from agentes.models import Agentes 
from faultmate.services.gemini_service import consultar_gemini

# Create your views here.
def home(request):
    return render(request, 'dashboard/index.html')

def login_view(request):
    return render(request, 'dashboard/registration/login.html')

def usuarios(request):
    usuarios = Usuario.objects.all()

    return render(
        request,
        'dashboard/usuarios.html',
        {
            'usuarios' : usuarios
        }
    )

def agentes(request):
    agentes = Agentes.objects.all()

    return render(
        request,
        'dashboard/agentes.html',
        {
            'agentes': agentes
        }
    )

def dashboard(request):
    total_diagnosticos = Diagnostico.objects.count()

    total_agentes = Agentes.objects.count()

    diagnosticos = Diagnostico.objects.all()

    context = {
    'total_diagnosticos': total_diagnosticos,
    'total_agentes': total_agentes,
    'diagnosticos' : diagnosticos
    }

    return render(request,'dashboard/dashboard.html', context)

def diagnosticos(request):
    return render(request, 'dashboard/diagnosticos.html')

def diagnosticar(request):

    resultado = None
    respuesta_gemini = None
    buscado = False

    if request.method == 'POST':

        buscado = True

        falla = request.POST.get('falla')

        resultado = Diagnostico.objects.filter(
            falla__icontains=falla
        ).first()

        if resultado is None:

           respuesta_gemini = consultar_gemini(falla)

           print("RESPUESTA GEMINI:")
           print(respuesta_gemini)

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