# Modelos (tablas de la base de datos) de la app "agentes".
# Cada clase se convierte en una tabla, y cada atributo en una columna.
from django.conf import settings
from django.db import models


class Agentes(models.Model):
    """Un agente IA que ayuda a diagnosticar fallas (ej. "Agente Motores")."""
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    # Instrucciones que se le daran a la IA (opcional).
    prompt = models.TextField(blank=True, null=True)

    # Que tan creativa es la IA al responder (0 = muy literal, 1 = muy creativa).
    temperatura = models.FloatField(default=0.7)

    # Limite de palabras/tokens que puede usar la IA en su respuesta.
    tokens = models.IntegerField(default=1000)

    # Indica si fue creado como agente base del sistema.
    es_base = models.BooleanField(default=False)

    def __str__(self):
        # Esto es lo que se muestra en el panel de administracion de Django.
        return self.nombre


class Falla(models.Model):
    """Una falla conocida de maquinaria industrial (ej. "Motor no arranca")."""
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre


class PreguntaDiagnostico(models.Model):
    """Pregunta que el sistema hace al tecnico para diagnosticar una Falla."""
    falla = models.ForeignKey(Falla, on_delete=models.CASCADE)
    pregunta = models.CharField(max_length=250)
    orden = models.IntegerField(default=1)  # En que orden se muestra la pregunta.

    def __str__(self):
        return self.pregunta


class CausaRaiz(models.Model):
    """Posible causa raiz de una Falla y su accion correctiva sugerida."""
    RESPUESTA_CHOICES = (
        ('si', 'Sí'),
        ('no', 'No'),
    )

    falla = models.ForeignKey(Falla, on_delete=models.CASCADE)
    pregunta_disparadora = models.ForeignKey(
        PreguntaDiagnostico,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='Si se define, esta causa aplica cuando esa pregunta tenga la respuesta indicada.',
    )
    respuesta_disparadora = models.CharField(max_length=2, choices=RESPUESTA_CHOICES, null=True, blank=True)
    causa = models.CharField(max_length=200)
    accion_correctiva = models.TextField()

    def __str__(self):
        return self.causa


class AgenteChatMensaje(models.Model):
    """Historial de conversacion por usuario y por agente."""
    ROLE_CHOICES = (
        ('user', 'Usuario'),
        ('assistant', 'Asistente'),
    )

    agente = models.ForeignKey(Agentes, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rol = models.CharField(max_length=20, choices=ROLE_CHOICES)
    contenido = models.TextField()
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['creado_en']

    def __str__(self):
        return f'{self.agente.nombre} - {self.rol}'


class AgenteEvento(models.Model):
    """Bitacora de eventos para analitica de agentes."""
    ACTION_CHOICES = (
        ('created_manual', 'Creado manual'),
        ('created_generated', 'Creado generado'),
        ('created_base', 'Creado base'),
        ('edited', 'Editado'),
        ('deleted', 'Eliminado'),
        ('chat_used', 'Usado en chat'),
    )

    agente = models.ForeignKey(Agentes, on_delete=models.SET_NULL, null=True, blank=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    accion = models.CharField(max_length=30, choices=ACTION_CHOICES)
    agente_nombre = models.CharField(max_length=120, blank=True)
    agente_es_base = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado_en']

    def __str__(self):
        return f'{self.accion} - {self.agente_nombre or "agente"}'