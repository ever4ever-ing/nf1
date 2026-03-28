from .auth import LoginForm, RegistroForm
from .mensaje_partido import MensajePartidoForm
from .partido import PartidoCrearForm, PartidoEditForm

# Compatibilidad
PartidoForm = PartidoCrearForm
from .recinto import RecintoForm
from .cancha import CanchaForm
from .equipo import EquipoForm
from .partido_competitivo import PartidoCompetitivoForm
from .invitacion_equipo import InvitacionEquipoForm
from .actualizar_resultado import ActualizarResultadoForm
from .asignar_numero_camiseta import AsignarNumeroCamisetaForm
from .reserva import ReservaForm
from .horario_cancha import HorarioCanchaForm
