# Generated by Django 2.2.5 on 2020-04-24 16:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inv', '0003_auto_20200424_1009'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='bodega_historico',
            unique_together={('bodega', 'fecha')},
        ),
        migrations.AlterUniqueTogether(
            name='sucursal_historico',
            unique_together={('sucursal', 'fecha')},
        ),
    ]
