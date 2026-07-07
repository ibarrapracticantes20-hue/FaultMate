# Migracion de datos: crea un usuario de PRUEBA para poder entrar al
# sistema apenas se clona el proyecto y se corre "migrate", sin tener
# que crear una cuenta a mano.
#
# Usuario: test
# Contrasena: test123
from django.contrib.auth.hashers import make_password
from django.db import migrations


def crear_usuario_prueba(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Usuario = apps.get_model('usuarios', 'Usuario')

    # Solo lo creamos si todavia no existe, para no duplicarlo si
    # alguien corre las migraciones mas de una vez.
    if not User.objects.filter(username='test').exists():
        User.objects.create(
            username='test',
            password=make_password('test123'),
            is_staff=False,
            is_superuser=False,
        )

    if not Usuario.objects.filter(correo='test@faultmate.com').exists():
        Usuario.objects.create(
            nombre='Usuario de Prueba',
            correo='test@faultmate.com',
            rol='Tecnico',
        )


def eliminar_usuario_prueba(apps, schema_editor):
    """Permite deshacer la migracion (borra al usuario de prueba)."""
    User = apps.get_model('auth', 'User')
    Usuario = apps.get_model('usuarios', 'Usuario')

    User.objects.filter(username='test').delete()
    Usuario.objects.filter(correo='test@faultmate.com').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0002_remove_usuario_activo_alter_usuario_correo_and_more'),
        ('auth', '__first__'),
    ]

    operations = [
        migrations.RunPython(crear_usuario_prueba, eliminar_usuario_prueba),
    ]
