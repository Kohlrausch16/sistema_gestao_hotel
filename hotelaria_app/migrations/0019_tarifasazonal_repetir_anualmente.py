from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotelaria_app', '0018_merge_20261114_1039'),
    ]

    operations = [
        migrations.AddField(
            model_name='tarifasazonal',
            name='repetir_anualmente',
            field=models.BooleanField(default=False),
        ),
    ]
