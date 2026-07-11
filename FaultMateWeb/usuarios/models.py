# Modelo (tabla) de la app "usuarios".
from django.contrib.auth.models import User
from django.db import models


class Usuario(models.Model):
    """Una persona que usa el sistema FaultMate (tecnico, administrador, etc.)."""
    ROLE_VISITANTE = 'VISITANTE'
    ROLE_ADMIN = 'ADMIN'
    ROLE_DESARROLLADOR = 'DESARROLLADOR'

    ROLE_CHOICES = [
        (ROLE_VISITANTE, 'Visitante'),
        (ROLE_ADMIN, 'Administrador'),
        (ROLE_DESARROLLADOR, 'Desarrollador'),
    ]

    nombre = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)  # No puede repetirse entre usuarios.
    rol = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_VISITANTE)
    auth_user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.nombre