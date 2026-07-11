from django import forms

from .models import Usuario


class UsuarioForm(forms.ModelForm):
    rol = forms.ChoiceField(choices=Usuario.ROLE_CHOICES)
    password = forms.CharField(required=False, widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ['nombre', 'correo', 'rol']

    def clean_correo(self):
        return self.cleaned_data['correo'].strip().lower()
