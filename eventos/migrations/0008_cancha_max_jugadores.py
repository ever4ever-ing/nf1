from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0007_usuario_permissions_recintos_gestion'),
    ]

    operations = [
        migrations.AddField(
            model_name='cancha',
            name='max_jugadores',
            field=models.PositiveSmallIntegerField(
                default=10,
                help_text='Cupo máximo de jugadores para partidos en esta cancha.',
            ),
        ),
    ]
