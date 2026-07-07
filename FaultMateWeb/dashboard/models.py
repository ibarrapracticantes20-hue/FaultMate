# Modelo (tabla) de la app "dashboard".
from django.db import models


class Diagnostico(models.Model):
    """
    Guarda cada diagnostico realizado: la falla que se escribio, el
    resultado obtenido y que agente lo genero (por ejemplo "Gemini IA").
    """
    falla = models.CharField(max_length=200)
    diagnostico = models.TextField()
    agente = models.CharField(max_length=100)
    fecha = models.DateTimeField(auto_now_add=True)  # Se llena solo al crearse.
    tiempo_diagnostico = models.IntegerField()  # Tiempo en minutos.

    def __str__(self):
        return self.falla
