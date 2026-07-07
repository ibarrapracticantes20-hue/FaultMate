from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('usuarios/', views.usuarios, name='usuarios'),
    path('agentes/', views.agentes, name='agentes'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('diagnosticos/', views.diagnosticos, name='diagnosticos'),
    path('diagnosticar/', views.diagnosticar, name='diagnosticar'),
    ] 
