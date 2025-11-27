from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Usuario, MensajePartido, Partido, Localidad, Recinto, Cancha, Equipo, PartidoCompetitivo, InvitacionEquipo, MiembroEquipo


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


# -----------------------
# Formularios integrados de canchas
# -----------------------
class RecintoForm(forms.ModelForm):
    class Meta:
        model = Recinto
        fields = ['nombre', 'direccion', 'id_localidad']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del recinto'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Dirección completa', 'rows': 3}),
            'id_localidad': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'nombre': 'Nombre del Recinto',
            'direccion': 'Dirección',
            'id_localidad': 'Localidad'
        }

class CanchaForm(forms.ModelForm):
    class Meta:
        model = Cancha
        fields = ['nombre', 'id_recinto', 'tipo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la cancha'}),
            'id_recinto': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Fútbol 11, Fútbol 7, Fútbol 5'}),
        }
        labels = {
            'nombre': 'Nombre de la Cancha',
            'id_recinto': 'Recinto',
            'tipo': 'Tipo de Cancha'
        }

# -----------------------
# Formularios integrados competitiva
# -----------------------
class EquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = ['nombre', 'logo', 'descripcion', 'color_primario', 'color_secundario']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del equipo'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe tu equipo...'}),
            'color_primario': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'color_secundario': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
        }

class PartidoCompetitivoForm(forms.ModelForm):
    fecha_hora = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )
    class Meta:
        model = PartidoCompetitivo
        fields = ['nombre', 'descripcion', 'id_equipo_visitante', 'id_cancha', 'id_localidad', 'lugar', 'fecha_hora']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del partido'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción del partido...'}),
            'id_equipo_visitante': forms.Select(attrs={'class': 'form-select'}),
            'id_cancha': forms.Select(attrs={'class': 'form-select'}),
            'id_localidad': forms.Select(attrs={'class': 'form-select'}),
            'lugar': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ubicación del partido'}),
        }

class InvitacionEquipoForm(forms.ModelForm):
    class Meta:
        model = InvitacionEquipo
        fields = ['id_usuario', 'mensaje']
        widgets = {
            'id_usuario': forms.Select(attrs={'class': 'form-select'}),
            'mensaje': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Mensaje de invitación...'}),
        }

class ActualizarResultadoForm(forms.ModelForm):
    class Meta:
        model = PartidoCompetitivo
        fields = ['goles_local', 'goles_visitante', 'estado']
        widgets = {
            'goles_local': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'goles_visitante': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

class AsignarNumeroCamisetaForm(forms.ModelForm):
    class Meta:
        model = MiembroEquipo
        fields = ['numero_camiseta']
        widgets = {
            'numero_camiseta': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 99, 'placeholder': 'Número'}),
        }
