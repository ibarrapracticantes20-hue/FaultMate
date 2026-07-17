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


class RegistroPublicoForm(forms.Form):
    nombre = forms.CharField(max_length=100)
    correo = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)

    def clean_correo(self):
        return self.cleaned_data['correo'].strip().lower()

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get('password')
        password_confirm = cleaned.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', 'Las contraseñas no coinciden.')
        return cleaned
