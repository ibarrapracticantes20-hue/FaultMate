from django.db import migrations


def marcar_agentes_base(apps, schema_editor):
    Agentes = apps.get_model('agentes', 'Agentes')
    nombres = ['Agente Motores', 'Agente Hidraulica', 'Agente Neumatica']
    Agentes.objects.filter(nombre__in=nombres).update(es_base=True)


class Migration(migrations.Migration):

    dependencies = [
        ('agentes', '0007_agentes_es_base_agenteevento'),
    ]

    operations = [
        migrations.RunPython(marcar_agentes_base, migrations.RunPython.noop),
    ]
