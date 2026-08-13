import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agentes', '0010_alter_causaraiz_respuesta_disparadora'),
    ]

    operations = [
        migrations.AddField(
            model_name='preguntadiagnostico',
            name='pregunta_padre',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='preguntas_hijas',
                to='agentes.preguntadiagnostico',
                help_text='Pregunta anterior de la que depende esta (vacío si es la primera pregunta de la falla).',
            ),
        ),
        migrations.AddField(
            model_name='preguntadiagnostico',
            name='respuesta_padre',
            field=models.CharField(
                blank=True,
                choices=[('si', 'Sí'), ('no', 'No')],
                max_length=2,
                null=True,
                help_text='Con qué respuesta de la pregunta padre se activa esta pregunta.',
            ),
        ),
        migrations.AddField(
            model_name='causaraiz',
            name='recomendacion_seguridad',
            field=models.TextField(blank=True, default=''),
        ),
    ]
