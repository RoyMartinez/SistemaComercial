# Generated by Django 2.2.5 on 2020-05-12 16:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inv', '0006_auto_20200429_1719'),
    ]

    operations = [
        migrations.AddField(
            model_name='kardex',
            name='bodega_fin',
            field=models.ForeignKey(default='ESTR', on_delete=django.db.models.deletion.CASCADE, related_name='Destinokardex', to='inv.Bodega'),
        ),
        migrations.AlterField(
            model_name='modelovehiculo',
            name='id_modelo',
            field=models.CharField(max_length=14, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='n3producto',
            name='aplicacion',
            field=models.ManyToManyField(default='NE.NEE000', to='inv.ModeloVehiculo'),
        ),
    ]
