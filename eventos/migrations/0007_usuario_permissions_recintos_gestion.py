# Generated manually for PermissionsMixin, recintos_gestion y grupo admin_recintos

from django.db import migrations, models


def crear_grupo_admin_recintos(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name='admin_recintos')


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('eventos', '0006_alter_reserva_fecha_reserva'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='is_superuser',
            field=models.BooleanField(
                default=False,
                help_text='Designates that this user has all permissions without explicitly assigning them.',
                verbose_name='superuser status',
            ),
        ),
        migrations.AddField(
            model_name='usuario',
            name='groups',
            field=models.ManyToManyField(
                blank=True,
                help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
                related_name='user_set',
                related_query_name='user',
                to='auth.group',
                verbose_name='groups',
            ),
        ),
        migrations.AddField(
            model_name='usuario',
            name='user_permissions',
            field=models.ManyToManyField(
                blank=True,
                help_text='Specific permissions for this user.',
                related_name='user_set',
                related_query_name='user',
                to='auth.permission',
                verbose_name='user permissions',
            ),
        ),
        migrations.AddField(
            model_name='usuario',
            name='recintos_gestion',
            field=models.ManyToManyField(
                blank=True,
                help_text='Recintos gestionables por usuarios del grupo admin_recintos (no aplica a superusuarios).',
                related_name='usuarios_admin_recintos',
                to='eventos.recinto',
                verbose_name='Recintos que administra',
            ),
        ),
        migrations.RunPython(crear_grupo_admin_recintos, migrations.RunPython.noop),
    ]
