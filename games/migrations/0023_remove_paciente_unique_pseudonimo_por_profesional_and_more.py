# games/migrations/0023_remove_paciente_unique_pseudonimo_por_profesional_and_more.py
from django.db import migrations

def limpiar_pacientes_huerfanos(apps, schema_editor):
    Paciente = apps.get_model('games', 'Paciente')
    Partida = apps.get_model('games', 'Partida')

    huerfanos = Paciente.objects.filter(profesional__isnull=True)
    partidas = Partida.objects.filter(paciente__in=huerfanos)
    
    print(f"[0023] Borrando {huerfanos.count()} pacientes y {partidas.count()} partidas huérfanas")
    
    partidas.delete()
    huerfanos.delete()

class Migration(migrations.Migration):
    dependencies = [
        ('games', '0022_perfiles_modalidad_perfiles_rol_and_more'),
    ]
    operations = [
        migrations.RunPython(limpiar_pacientes_huerfanos, migrations.RunPython.noop),
    ]