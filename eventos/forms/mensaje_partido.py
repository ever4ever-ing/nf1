from django import forms

from ..models import MensajePartido


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
