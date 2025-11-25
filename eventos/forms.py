from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Usuario, MensajePartido, Partido, Localidad


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'tu@email.com',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '••••••••'
        })
    )


class RegistroForm(forms.ModelForm):
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '••••••••'
        })
    )
    password_confirm = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '••••••••'
        })
    )
    
    class Meta:
        model = Usuario
        fields = ['nombre', 'apellido', 'email']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'tu@email.com'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        
        return cleaned_data
    
    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data['password'])
        if commit:
            usuario.save()
        return usuario


class MensajePartidoForm(forms.ModelForm):
    class Meta:
        model = MensajePartido
        fields = ['mensaje']
        widgets = {
            'mensaje': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Escribe tu mensaje aquí...',
                'rows': 3
            })
        }
        labels = {
            'mensaje': ''
        }


class PartidoForm(forms.ModelForm):
    fecha_inicio = forms.DateTimeField(
        label='Fecha y Hora',
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local',
            'placeholder': 'Selecciona fecha y hora'
        }),
        input_formats=['%Y-%m-%dT%H:%M']
    )
    
    class Meta:
        model = Partido
        fields = ['lugar', 'fecha_inicio', 'id_localidad', 'max_jugadores', 'descripcion']
        widgets = {
            'lugar': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Cancha Municipal, Estadio Central'
            }),
            'id_localidad': forms.Select(attrs={
                'class': 'form-select'
            }),
            'max_jugadores': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '2',
                'max': '100',
                'value': '10'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe tu partido: nivel, reglas, qué llevar, etc.',
                'rows': 4
            }),
        }
        labels = {
            'lugar': 'Lugar del Partido',
            'fecha_inicio': 'Fecha y Hora',
            'id_localidad': 'Localidad',
            'max_jugadores': 'Máximo de Jugadores',
            'descripcion': 'Descripción'
        }
