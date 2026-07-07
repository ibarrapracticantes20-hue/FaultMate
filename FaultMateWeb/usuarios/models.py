# Modelo (tabla) de la app "usuarios".
from django.db import models


class Usuario(models.Model):
    """Una persona que usa el sistema FaultMate (tecnico, administrador, etc.)."""
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)  # No puede repetirse entre usuarios.
    rol = models.CharField(max_length=50, default="Tecnico")

    def __str__(self):
        return self.nombre