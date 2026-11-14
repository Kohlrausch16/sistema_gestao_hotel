import django.db.models.deletion
from django.db import migrations, models


def migrar_tipos(apps, schema_editor):
    Quarto = apps.get_model('hotelaria_app', 'Quarto')
    TipoQuarto = apps.get_model('hotelaria_app', 'TipoQuarto')
    banco = schema_editor.connection.alias
    nomes = {'S': 'Simples', 'D': 'Duplo', 'U': 'Suíte', 'T': 'Triplo'}

    codigos = set(Quarto.objects.using(banco).values_list('tipo', flat=True).distinct())
    desconhecidos = codigos - nomes.keys()
    if desconhecidos:
        raise ValueError(f'Tipos de quarto desconhecidos: {sorted(desconhecidos)}')

    for codigo in sorted(codigos):
        tipo = TipoQuarto.objects.using(banco).create(
            tipo=nomes[codigo], preco_diaria=0, tarifa_adicional=0
        )
        Quarto.objects.using(banco).filter(tipo=codigo).update(tipo_quarto=tipo)


class Migration(migrations.Migration):
    dependencies = [
        ('hotelaria_app', '0011_ocorrencia_concluida'),
    ]

    operations = [
        migrations.CreateModel(
            name='TipoQuarto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(max_length=20)),
                ('preco_diaria', models.DecimalField(decimal_places=2, max_digits=10)),
                ('tarifa_adicional', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
            ],
        ),
        migrations.AddField(
            model_name='quarto',
            name='tipo_quarto',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='hotelaria_app.tipoquarto'),
        ),
        migrations.RunPython(migrar_tipos),
        migrations.RemoveField(model_name='quarto', name='tipo'),
        migrations.RenameField(model_name='quarto', old_name='tipo_quarto', new_name='tipo'),
        migrations.AlterField(
            model_name='quarto',
            name='tipo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='hotelaria_app.tipoquarto'),
        ),
    ]
