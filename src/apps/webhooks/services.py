import json
import logging
import threading
import urllib.request
import urllib.error
from typing import Dict, Any, Optional
from django.utils import timezone
from .models import Webhook

logger = logging.getLogger(__name__)


class WebhookService:
    @staticmethod
    def dispatch_event(event_type: str, payload: Dict[str, Any], user: Optional[Any] = None) -> None:
        """
        Dispatch a webhook event to active matching webhook URLs.
        Runs in a background thread to prevent blocking HTTP response loops.
        """
        def _normalize_event(evt_str: str) -> str:
            s = evt_str.upper().replace(".", "_")
            for plural, singular in [
                ("PARTICIPANTS_", "PARTICIPANT_"),
                ("TRANSCRIPTS_", "TRANSCRIPT_"),
                ("RECORDINGS_", "RECORDING_"),
                ("SUMMARIES_", "SUMMARY_"),
                ("MEETINGS_", "MEETING_"),
            ]:
                if s.startswith(plural):
                    s = singular + s[len(plural):]
            return s

        def _send():
            try:
                norm_event = _normalize_event(event_type)
                query = Webhook.objects.filter(is_active=True)
                if user and hasattr(user, 'is_authenticated') and user.is_authenticated:
                    query = query.filter(user=user)
                
                all_hooks = list(query)
                webhooks = [
                    h for h in all_hooks 
                    if _normalize_event(h.event) == norm_event
                ]
                if not webhooks:
                    return

                data = {
                    "event": event_type,
                    "timestamp": timezone.now().isoformat(),
                    "payload": payload
                }
                body = json.dumps(data).encode('utf-8')
                headers = {
                    "Content-Type": "application/json",
                    "User-Agent": "MeetFlow-Webhook-Dispatcher/1.0"
                }

                for webhook in webhooks:
                    try:
                        req = urllib.request.Request(webhook.url, data=body, headers=headers, method="POST")
                        with urllib.request.urlopen(req, timeout=5) as resp:
                            logger.info(f"Webhook {event_type} delivered to {webhook.url} -> HTTP Status {resp.getcode()}")
                    except Exception as e:
                        logger.error(f"Failed to dispatch webhook {event_type} to {webhook.url}: {e}")
            except Exception as outer_e:
                logger.error(f"Error in webhook dispatch thread for {event_type}: {outer_e}")

        # Dispatch async in background thread
        t = threading.Thread(target=_send, daemon=True)
        t.start()

    @classmethod
    def notify_meeting_created(cls, meeting) -> None:
        """Trigger MEETING_CREATED webhook event."""
        payload = {
            "meeting_id": meeting.meeting_id,
            "room_code": meeting.room_code,
            "title": meeting.title,
            "meeting_type": meeting.meeting_type,
            "status": meeting.status,
            "host_id": meeting.host.id,
            "host_email": meeting.host.email,
            "start_time": meeting.start_time.isoformat() if meeting.start_time else None,
            "created_at": meeting.created_at.isoformat() if meeting.created_at else None,
        }
        cls.dispatch_event("MEETING_CREATED", payload, user=meeting.host)

    @classmethod
    def notify_meeting_started(cls, meeting) -> None:
        """Trigger MEETING_STARTED webhook event."""
        payload = {
            "meeting_id": meeting.meeting_id,
            "room_code": meeting.room_code,
            "title": meeting.title,
            "status": meeting.status,
            "started_at": timezone.now().isoformat(),
            "host_id": meeting.host.id,
        }
        cls.dispatch_event("MEETING_STARTED", payload, user=meeting.host)

    @classmethod
    def notify_meeting_ended(cls, meeting) -> None:
        """Trigger MEETING_ENDED webhook event."""
        payload = {
            "meeting_id": meeting.meeting_id,
            "room_code": meeting.room_code,
            "title": meeting.title,
            "status": meeting.status,
            "ended_at": meeting.end_time.isoformat() if meeting.end_time else timezone.now().isoformat(),
            "host_id": meeting.host.id,
        }
        cls.dispatch_event("MEETING_ENDED", payload, user=meeting.host)

    @classmethod
    def notify_participant_joined(cls, meeting, participant) -> None:
        """Trigger PARTICIPANT_JOINED / participants.joined webhook event."""
        participant_name = (
            participant.user.get_full_name() if (participant.user and participant.user.get_full_name())
            else (participant.user.email if participant.user else (participant.guest_name or "Guest"))
        )
        payload = {
            "meeting_id": meeting.meeting_id,
            "room_code": meeting.room_code,
            "title": meeting.title,
            "participant_id": participant.id,
            "participant_name": participant_name,
            "role": participant.role,
            "status": participant.status,
            "joined_at": participant.joined_at.isoformat() if getattr(participant, 'joined_at', None) else timezone.now().isoformat(),
            "host_id": meeting.host.id,
        }
        cls.dispatch_event("PARTICIPANT_JOINED", payload, user=meeting.host)

    @classmethod
    def notify_participant_left(cls, meeting, participant, reason: str = "left") -> None:
        """Trigger PARTICIPANT_LEFT / participants.left webhook event."""
        participant_name = (
            participant.user.get_full_name() if (participant.user and participant.user.get_full_name())
            else (participant.user.email if participant.user else (participant.guest_name or "Guest"))
        )
        payload = {
            "meeting_id": meeting.meeting_id,
            "room_code": meeting.room_code,
            "title": meeting.title,
            "participant_id": participant.id,
            "participant_name": participant_name,
            "role": participant.role,
            "reason": reason,
            "left_at": timezone.now().isoformat(),
            "host_id": meeting.host.id,
        }
        cls.dispatch_event("PARTICIPANT_LEFT", payload, user=meeting.host)

    @classmethod
    def notify_recording_completed(cls, recording_instance) -> None:
        """Trigger RECORDING_READY and RECORDING_COMPLETED webhook events."""
        meeting = recording_instance.meeting
        payload = {
            "recording_id": recording_instance.id,
            "meeting_id": meeting.meeting_id,
            "room_code": meeting.room_code,
            "title": meeting.title,
            "host_id": meeting.host.id,
            "file_path": getattr(recording_instance, 'file_path', str(getattr(recording_instance, 'file', ''))),
            "created_at": recording_instance.created_at.isoformat() if getattr(recording_instance, 'created_at', None) else timezone.now().isoformat(),
        }
        cls.dispatch_event("RECORDING_READY", payload, user=meeting.host)
        cls.dispatch_event("RECORDING_COMPLETED", payload, user=meeting.host)

    @classmethod
    def notify_transcript_completed(cls, meeting, utterance_count: int = 0) -> None:
        """Trigger TRANSCRIPT_READY and TRANSCRIPT_COMPLETED webhook events."""
        payload = {
            "meeting_id": meeting.meeting_id,
            "room_code": meeting.room_code,
            "title": meeting.title,
            "host_id": meeting.host.id,
            "utterance_count": utterance_count,
            "completed_at": timezone.now().isoformat(),
        }
        cls.dispatch_event("TRANSCRIPT_READY", payload, user=meeting.host)
        cls.dispatch_event("TRANSCRIPT_COMPLETED", payload, user=meeting.host)

    @classmethod
    def notify_summary_completed(cls, meeting, summary_instance=None) -> None:
        """Trigger SUMMARY_READY and SUMMARY_COMPLETED webhook events."""
        payload = {
            "meeting_id": meeting.meeting_id,
            "room_code": meeting.room_code,
            "title": meeting.title,
            "host_id": meeting.host.id,
            "summary_text": getattr(summary_instance, 'summary_text', '') if summary_instance else '',
            "completed_at": timezone.now().isoformat(),
        }
        cls.dispatch_event("SUMMARY_READY", payload, user=meeting.host)
        cls.dispatch_event("SUMMARY_COMPLETED", payload, user=meeting.host)

    @classmethod
    def notify_youtube_upload_completed(cls, recording_instance, video_url: str = "", video_id: str = "") -> None:
        """Trigger YOUTUBE_UPLOAD_COMPLETED / youtube.upload.completed webhook event."""
        meeting = recording_instance.meeting
        payload = {
            "recording_id": recording_instance.id,
            "meeting_id": meeting.meeting_id,
            "room_code": meeting.room_code,
            "title": meeting.title,
            "video_url": video_url,
            "video_id": video_id,
            "host_id": meeting.host.id,
            "completed_at": timezone.now().isoformat(),
        }
        cls.dispatch_event("YOUTUBE_UPLOAD_COMPLETED", payload, user=meeting.host)
