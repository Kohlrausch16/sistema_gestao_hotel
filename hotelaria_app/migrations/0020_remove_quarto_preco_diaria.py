from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hotelaria_app', '0019_tarifasazonal_repetir_anualmente'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quarto',
            name='preco_diaria',
        ),
    ]
