# games/migrations/0025_alter_paciente_constraints.py

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('games', '0024_paciente_user'), 
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='paciente',
            name='unique_pseudonimo_por_profesional',
        ),
        migrations.AlterField(
            model_name='paciente',
            name='institucion',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='pacientes', to='games.institucion'),
        ),
        migrations.AlterField(
            model_name='paciente',
            name='profesional',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='pacientes_asignados', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddConstraint(
            model_name='paciente',
            constraint=models.UniqueConstraint(fields=('profesional', 'pseudonimo_hash'), name='unique_pseudonimo_por_profesional'),
        ),
    ]