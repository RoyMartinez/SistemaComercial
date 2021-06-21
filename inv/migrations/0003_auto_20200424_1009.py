# Generated by Django 2.2.5 on 2020-04-24 10:09

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inv', '0002_auto_20200424_1008'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bodega',
            name='existencia',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='bodega',
            name='saldo',
            field=models.FloatField(blank=True, default=0, null=True, validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
        migrations.AlterField(
            model_name='sucursal',
            name='existencia',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='sucursal',
            name='saldo',
            field=models.FloatField(blank=True, default=0, null=True, validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
    ]
