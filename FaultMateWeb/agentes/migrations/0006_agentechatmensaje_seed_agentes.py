import django.db.models.deletion
from django.db import migrations, models


def seed_agentes_base(apps, schema_editor):
    Agentes = apps.get_model('agentes', 'Agentes')

    data = [
        {
            'nombre': 'Agente Motores',
            'descripcion': 'Agente especializado en mantenimiento industrial para motores electricos.',
            'prompt': 'Eres Agente Motores. Analiza fallas de motores electricos y responde con diagnostico, causa raiz y accion recomendada.',
            'temperatura': 0.5,
            'tokens': 900,
        },
        {
            'nombre': 'Agente Hidraulica',
            'descripcion': 'Agente especializado en sistemas hidraulicos para bombas y actuadores.',
            'prompt': 'Eres Agente Hidraulica. Analiza fallas hidraulicas y responde con diagnostico, causa raiz y accion recomendada.',
            'temperatura': 0.5,
            'tokens': 900,
        },
        {
            'nombre': 'Agente Neumatica',
            'descripcion': 'Agente especializado en sistemas neumaticos para cilindros y valvulas.',
            'prompt': 'Eres Agente Neumatica. Analiza fallas neumaticas y responde con diagnostico, causa raiz y accion recomendada.',
            'temperatura': 0.4,
            'tokens': 700,
        },
    ]

    for item in data:
        Agentes.objects.get_or_create(
            nombre=item['nombre'],
            defaults={
                'descripcion': item['descripcion'],
                'prompt': item['prompt'],
                'temperatura': item['temperatura'],
                'tokens': item['tokens'],
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('agentes', '0004_alter_agentes_id_alter_causaraiz_id_alter_falla_id_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='AgenteChatMensaje',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rol', models.CharField(choices=[('user', 'Usuario'), ('assistant', 'Asistente')], max_length=20)),
                ('contenido', models.TextField()),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('agente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='agentes.agentes')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={
                'ordering': ['creado_en'],
            },
        ),
        migrations.RunPython(seed_agentes_base, migrations.RunPython.noop),
    ]
