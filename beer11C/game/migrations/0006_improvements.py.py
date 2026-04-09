# game/migrations/XXXX_improvements.py
# Number this after your last migration (e.g. 0003_improvements.py)
# Run: python manage.py migrate

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        # ↑ Replace 'game' below with your actual app name if different
        ('game', '0002_add_playersession_phase_fields'),
        # ↑ Replace with YOUR last migration name
    ]

    operations = [
        # GameSession.created_by
        migrations.AddField(
            model_name='gamesession',
            name='created_by',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='created_games',
                to='auth.user',
            ),
        ),
        # PlayerSession.user
        migrations.AddField(
            model_name='playersession',
            name='user',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='player_sessions',
                to='auth.user',
            ),
        ),
        # PlayerSession.disconnected_at
        migrations.AddField(
            model_name='playersession',
            name='disconnected_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        # PlayerSession.last_week_summary
        migrations.AddField(
            model_name='playersession',
            name='last_week_summary',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
