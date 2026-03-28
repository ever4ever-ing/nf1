"""Permisos: recintos solo administradores del sitio; canchas/horarios también grupo admin_recintos."""

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import Cancha, Recinto

GRUPO_ADMIN_RECINTOS = 'admin_recintos'


def _es_staff_sitio(user) -> bool:
    return bool(getattr(user, 'is_admin', False))


def usuario_es_admin_sitio(user) -> bool:
    """Gestión de recintos (CRUD): solo superusuario o staff del sitio (is_admin)."""
    if not user.is_authenticated:
        return False
    return user.is_superuser or _es_staff_sitio(user)


def usuario_grupo_admin_recintos(user) -> bool:
    if not user.is_authenticated:
        return False
    return user.groups.filter(name=GRUPO_ADMIN_RECINTOS).exists()


def usuario_puede_gestionar_canchas(user) -> bool:
    """Canchas y horarios: administrador del sitio o miembro del grupo admin_recintos."""
    if not user.is_authenticated:
        return False
    if usuario_es_admin_sitio(user):
        return True
    return usuario_grupo_admin_recintos(user)


def recintos_para_dropdown_cancha(user):
    """Recintos elegibles al crear/editar una cancha (admin: todos; admin_recintos: los asignados)."""
    if not user.is_authenticated:
        return Recinto.objects.none()
    if usuario_es_admin_sitio(user):
        return Recinto.objects.all()
    return user.recintos_gestion.all()


def puede_gestionar_cancha(user, cancha: Cancha) -> bool:
    if not usuario_puede_gestionar_canchas(user):
        return False
    if usuario_es_admin_sitio(user):
        return True
    return user.recintos_gestion.filter(pk=cancha.id_recinto_id).exists()


def mapa_puede_editar_canchas(user, canchas):
    if not usuario_puede_gestionar_canchas(user):
        return {}
    if usuario_es_admin_sitio(user):
        return {c.id_cancha: True for c in canchas}
    permitidos = set(user.recintos_gestion.values_list('pk', flat=True))
    return {
        c.id_cancha: c.id_recinto_id in permitidos
        for c in canchas
    }


def contexto_edicion_canchas(user, canchas):
    if not usuario_puede_gestionar_canchas(user):
        return {'canchas_editables_todas': False, 'ids_canchas_editables': []}
    if usuario_es_admin_sitio(user):
        return {'canchas_editables_todas': True, 'ids_canchas_editables': []}
    m = mapa_puede_editar_canchas(user, canchas)
    ids = [k for k, v in m.items() if v]
    return {'canchas_editables_todas': False, 'ids_canchas_editables': ids}


class SoloAdminSitioMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Solo superusuario o is_admin (gestión de recintos)."""

    def test_func(self):
        return usuario_es_admin_sitio(self.request.user)


class GestionCanchasMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Administrador del sitio o grupo admin_recintos (canchas y horarios)."""

    def test_func(self):
        return usuario_puede_gestionar_canchas(self.request.user)
