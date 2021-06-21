# Generated by Django 2.2.5 on 2020-04-23 15:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('inv', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LoggedInUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(blank=True, max_length=32, null=True)),
                ('sucursal', models.ForeignKey(default='DU', on_delete=django.db.models.deletion.CASCADE, to='inv.Sucursal')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='logged_in_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
