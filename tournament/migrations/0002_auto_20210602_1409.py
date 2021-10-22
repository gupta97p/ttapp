# Generated by Django 3.1.2 on 2021-06-02 08:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tournament', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='tournament',
            name='player',
            field=models.ManyToManyField(blank=True, default=list, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='tournament',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_reg4', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='setdata',
            name='match',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tournament.matchdata'),
        ),
        migrations.AddField(
            model_name='setdata',
            name='set_winner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='matchdata',
            name='player1',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_reg1', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='matchdata',
            name='player2',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_reg2', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='matchdata',
            name='tournament',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='tournament.tournament'),
        ),
        migrations.AddField(
            model_name='matchdata',
            name='winner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
