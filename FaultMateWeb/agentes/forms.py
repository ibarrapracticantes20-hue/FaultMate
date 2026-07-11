from django import forms

from .models import Agentes


class AgenteForm(forms.ModelForm):
    class Meta:
        model = Agentes
        fields = ['nombre', 'descripcion', 'prompt', 'temperatura', 'tokens']

    def clean_temperatura(self):
        temperatura = self.cleaned_data['temperatura']
        if temperatura < 0 or temperatura > 1:
            raise forms.ValidationError('La temperatura debe estar entre 0 y 1.')
        return temperatura

    def clean_tokens(self):
        tokens = self.cleaned_data['tokens']
        if tokens < 50:
            raise forms.ValidationError('El limite minimo de tokens es 50.')
        return tokens


class GenerarAgenteForm(forms.Form):
    nombre = forms.CharField(max_length=100)
    dominio = forms.CharField(
        max_length=120,
        initial='Mantenimiento industrial',
        help_text='Ejemplo: Mantenimiento hidraulico, lineas de ensamble, compresores.',
    )
    tipo_maquina = forms.CharField(max_length=120, initial='Motores electricos')
    nivel_detalle = forms.ChoiceField(
        choices=[
            ('basico', 'Basico'),
            ('intermedio', 'Intermedio'),
            ('avanzado', 'Avanzado'),
        ],
        initial='intermedio',
    )
    estilo = forms.ChoiceField(
        choices=[
            ('tecnico', 'Tecnico'),
            ('practico', 'Practico'),
            ('didactico', 'Didactico'),
        ],
        initial='tecnico',
    )
