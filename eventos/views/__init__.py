from .auth import login_view, logout_view, registro_view
from .base import home, index, ranking_usuarios, ver_perfil_usuario
from .canchas_reservas import (
    api_horarios_disponibles,
    cancelar_reserva,
    crear_cancha,
    crear_recinto,
    crear_reserva,
    disponibilidad_cancha,
    editar_cancha,
    editar_recinto,
    gestionar_horarios_cancha,
    lista_canchas,
    lista_recintos,
    mis_canchas_admin,
    mis_reservas,
)
from .competitiva import (
    crear_equipo,
    crear_partido_competitivo,
    detalle_equipo,
    detalle_partido_competitivo,
    editar_equipo,
    invitar_miembro,
    lista_equipos,
    lista_partidos_competitivos,
    mis_equipos,
    mis_invitaciones,
    responder_invitacion,
    salir_equipo,
)
from .notificaciones import (
    marcar_notificacion_leida,
    marcar_todas_leidas,
    mis_notificaciones,
    obtener_notificaciones_nuevas,
)
from .partidos import (
    cancelar_partido,
    crear_partido,
    detalle_partido,
    editar_partido,
    lista_partidos,
    mis_partidos,
    salir_partido,
    unirse_partido,
)
from .perfil import editar_perfil, mi_perfil
