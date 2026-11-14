from django.db import migrations


def criar_tipos_padrao(apps, schema_editor):
    TipoQuarto = apps.get_model('hotelaria_app', 'TipoQuarto')
    banco = schema_editor.connection.alias
    for nome in ('Simples', 'Duplo', 'Suíte'):
        TipoQuarto.objects.using(banco).get_or_create(
            tipo=nome,
            defaults={'preco_diaria': 0, 'tarifa_adicional': 0},
        )


class Migration(migrations.Migration):
    dependencies = [
        ('hotelaria_app', '0012_tipoquarto_alter_quarto_tipo'),
    ]

    operations = [
        migrations.RunPython(criar_tipos_padrao),
    ]
