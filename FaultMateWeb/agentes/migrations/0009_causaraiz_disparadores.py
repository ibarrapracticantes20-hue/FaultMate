from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('agentes', '0008_marcar_agentes_base'),
    ]

    operations = [
        migrations.AddField(
            model_name='causaraiz',
            name='pregunta_disparadora',
            field=models.ForeignKey(blank=True, help_text='Si se define, esta causa aplica cuando esa pregunta tenga la respuesta indicada.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='agentes.preguntadiagnostico'),
        ),
        migrations.AddField(
            model_name='causaraiz',
            name='respuesta_disparadora',
            field=models.CharField(blank=True, choices=[('si', 'Si'), ('no', 'No')], max_length=2, null=True),
        ),
    ]
