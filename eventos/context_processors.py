from .admin_recintos import usuario_es_admin_sitio, usuario_puede_gestionar_canchas


def nav_admin_recintos(request):
    u = request.user
    return {
        'es_admin_sitio': usuario_es_admin_sitio(u),
        'puede_gestionar_canchas': usuario_puede_gestionar_canchas(u),
    }
