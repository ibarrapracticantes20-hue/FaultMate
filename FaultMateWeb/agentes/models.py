from django.db import models


class Agentes(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    prompt = models.TextField(
        blank=True,
        null=True
    )

    temperatura = models.FloatField(default=0.7)

    tokens = models.IntegerField(default=1000)

    def __str__(self):
        return self.nombre


class Falla(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre


class PreguntaDiagnostico(models.Model):
    falla = models.ForeignKey(
        Falla,
        on_delete=models.CASCADE
    )

    pregunta = models.CharField(max_length=250)

    orden = models.IntegerField(default=1)

    def __str__(self):
        return self.pregunta


class CausaRaiz(models.Model):
    falla = models.ForeignKey(
        Falla,
        on_delete=models.CASCADE
    )

    causa = models.CharField(max_length=200)
    accion_correctiva = models.TextField()

    def __str__(self):
        return self.causa