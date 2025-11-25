from django import forms
from .models import Equipo, PartidoCompetitivo, InvitacionEquipo, MiembroEquipo


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
            'fecha_hora': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
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
