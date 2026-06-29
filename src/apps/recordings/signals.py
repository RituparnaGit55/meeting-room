from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Recording
from apps.meetings.models import MeetingRecording

@receiver(post_save, sender=Recording)
def trigger_transcription_for_recording(sender, instance, created, **kwargs):
    if created:
        from apps.transcripts.tasks import process_transcription
        process_transcription.delay(instance.id, recording_model="Recording")

        # Notify host: Recording Ready
        try:
            from apps.notifications.services import NotificationService
            NotificationService.notify_host(
                meeting=instance.meeting,
                notification_type="RECORDING_READY",
                title="Recording Ready",
                message=f"A recording for meeting '{instance.meeting.title}' has been saved and is being processed.",
            )
        except Exception as e:
            print(f"Failed to send recording notification: {e}")

@receiver(post_save, sender=MeetingRecording)
def trigger_transcription_for_meeting_recording(sender, instance, created, **kwargs):
    if created:
        from apps.transcripts.tasks import process_transcription
        process_transcription.delay(instance.id, recording_model="MeetingRecording")

        # Notify host: Recording Ready
        try:
            from apps.notifications.services import NotificationService
            NotificationService.notify_host(
                meeting=instance.meeting,
                notification_type="RECORDING_READY",
                title="Recording Ready",
                message=f"A recording for meeting '{instance.meeting.title}' has been saved and is being processed.",
            )
        except Exception as e:
            print(f"Failed to send recording notification: {e}")
