
from django.db import migrations, models
import django.utils.timezone
import secrets

class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Meeting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('meeting_type', models.CharField(choices=[('INSTANT', 'Instant Meeting'), ('SCHEDULED', 'Scheduled Meeting'), ('RECURRING', 'Recurring Meeting')], default='SCHEDULED', max_length=20)),
                ('room_code', models.CharField(editable=False, max_length=12, unique=True)),
                ('meeting_id', models.CharField(editable=False, max_length=20, unique=True)),
                ('password', models.CharField(blank=True, max_length=20, null=True)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('duration', models.IntegerField(blank=True, help_text='Duration in minutes', null=True)),
                ('status', models.CharField(choices=[('SCHEDULED', 'Scheduled'), ('IN_PROGRESS', 'In Progress'), ('COMPLETED', 'Completed'), ('CANCELLED', 'Cancelled')], default='SCHEDULED', max_length=20)),
                ('is_recording', models.BooleanField(default=False)),
                ('enable_waiting_room', models.BooleanField(default=False)),
                ('recurrence_pattern', models.CharField(choices=[('NONE', 'None'), ('DAILY', 'Daily'), ('WEEKLY', 'Weekly'), ('MONTHLY', 'Monthly')], default='NONE', max_length=20)),
                ('recurrence_end_date', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('host', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hosted_meetings', to='accounts.user')),
            ],
        ),
        migrations.CreateModel(
            name='MeetingParticipant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('guest_name', models.CharField(blank=True, max_length=255, null=True)),
                ('role', models.CharField(choices=[('HOST', 'Host'), ('CO_HOST', 'Co-Host'), ('PARTICIPANT', 'Participant'), ('GUEST', 'Guest')], default='PARTICIPANT', max_length=20)),
                ('status', models.CharField(choices=[('WAITING', 'Waiting Room'), ('JOINED', 'Joined'), ('LEFT', 'Left'), ('REMOVED', 'Removed')], default='JOINED', max_length=20)),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('left_at', models.DateTimeField(blank=True, null=True)),
                ('is_screen_sharing', models.BooleanField(default=False)),
                ('is_video_on', models.BooleanField(default=True)),
                ('is_audio_on', models.BooleanField(default=True)),
                ('has_raised_hand', models.BooleanField(default=False)),
                ('hand_raised_at', models.DateTimeField(blank=True, null=True)),
                ('meeting', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participants', to='meetings.meeting')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='participated_meetings', to='accounts.user')),
            ],
            options={
                'ordering': ['-joined_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='meetingparticipant',
            constraint=models.UniqueConstraint(fields=('meeting', 'user'), name='unique_meeting_user_participant'),
        ),
    ]
