# Modelos (tablas de la base de datos) de la app "agentes".
# Cada clase se convierte en una tabla, y cada atributo en una columna.
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
    falla = models.ForeignKey(Falla, on_delete=models.CASCADE)
    causa = models.CharField(max_length=200)
    accion_correctiva = models.TextField()

    def __str__(self):
        return self.causa