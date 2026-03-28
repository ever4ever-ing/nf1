from django import forms

from ..models import InvitacionEquipo


class InvitacionEquipoForm(forms.ModelForm):
    class Meta:
        model = InvitacionEquipo
        fields = ['id_usuario', 'mensaje']
        widgets = {
            'id_usuario': forms.Select(attrs={'class': 'form-select'}),
            'mensaje': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Mensaje de invitación...'}),
        }
