from django.db import models

class Diagnostico(models.Model):
  falla = models.CharField(max_length=200)
  diagnostico = models.TextField()
  agente = models.CharField(max_length=100)
  fecha = models.DateTimeField(auto_now_add=True)
  tiempo_diagnostico = models.IntegerField()

  def __str__(self):
      return self.falla
