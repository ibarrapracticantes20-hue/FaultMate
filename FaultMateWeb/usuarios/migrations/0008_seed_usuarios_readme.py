from django.contrib.auth.hashers import make_password
from django.db import migrations


USUARIOS_SEMILLA = [
    ('genadmin@example.com', 'Gen Admin', 'DESARROLLADOR'),
    ('crudadmin@example.com', 'Crud Admin', 'DESARROLLADOR'),
    ('visitante@example.com', 'Visitante QA', 'VISITANTE'),
    ('chatqa@example.com', 'Chat QA', 'VISITANTE'),
    ('homeqa@example.com', 'Home QA', 'VISITANTE'),
    ('layoutqa@example.com', 'Layout QA', 'VISITANTE'),
    ('dashqa@example.com', 'Dashboard QA', 'VISITANTE'),
]

PASSWORD_POR_DEFECTO = 'test1234'


def seed_usuarios_readme(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Usuario = apps.get_model('usuarios', 'Usuario')

    for correo, nombre, rol in USUARIOS_SEMILLA:
        auth_user, _ = User.objects.get_or_create(
            username=correo,
            defaults={
                'email': correo,
            },
        )

        auth_user.email = correo
        auth_user.password = make_password(PASSWORD_POR_DEFECTO)
        auth_user.is_staff = rol in ['ADMIN', 'DESARROLLADOR']
        auth_user.is_superuser = rol == 'DESARROLLADOR'
        auth_user.save()

        Usuario.objects.update_or_create(
            correo=correo,
            defaults={
                'nombre': nombre,
                'rol': rol,
                'auth_user': auth_user,
            },
        )


def unseed_usuarios_readme(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Usuario = apps.get_model('usuarios', 'Usuario')

    correos = [correo for correo, _, _ in USUARIOS_SEMILLA]
    Usuario.objects.filter(correo__in=correos).delete()
    User.objects.filter(username__in=correos).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0007_alter_usuario_rol'),
        ('auth', '__first__'),
    ]

    operations = [
        migrations.RunPython(seed_usuarios_readme, unseed_usuarios_readme),
    ]
