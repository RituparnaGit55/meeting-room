from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Recording
from apps.meetings.models import MeetingRecording

@receiver(post_save, sender=Recording)
def trigger_transcription_for_recording(sender, instance, created, **kwargs):
    if created:
        from apps.transcripts.tasks import process_transcription
        process_transcription.delay(instance.id, recording_model="Recording")

@receiver(post_save, sender=MeetingRecording)
def trigger_transcription_for_meeting_recording(sender, instance, created, **kwargs):
    if created:
        from apps.transcripts.tasks import process_transcription
        process_transcription.delay(instance.id, recording_model="MeetingRecording")
