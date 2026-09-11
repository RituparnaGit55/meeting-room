
from django.utils import timezone
from apps.accounts.models import User
from apps.meetings.models import Meeting, MeetingParticipant
from apps.meetings.repositories.meeting_repository import (
    MeetingRepository, MeetingParticipantRepository
)
from apps.webhooks.services import WebhookService


class MeetingService:
    @staticmethod
    def create_instant_meeting(title: str, host: User, **kwargs) -> Meeting:
        meeting = MeetingRepository.create_meeting({
            'title': title,
            'meeting_type': 'INSTANT',
            'start_time': timezone.now(),
            'status': 'IN_PROGRESS',
            **kwargs
        }, host)
        try:
            WebhookService.notify_meeting_created(meeting)
            WebhookService.notify_meeting_started(meeting)
        except Exception:
            pass
        return meeting

    @staticmethod
    def create_scheduled_meeting(title: str, start_time, host: User, **kwargs) -> Meeting:
        meeting = MeetingRepository.create_meeting({
            'title': title,
            'meeting_type': 'SCHEDULED',
            'start_time': start_time,
            **kwargs
        }, host)
        try:
            WebhookService.notify_meeting_created(meeting)
        except Exception:
            pass
        return meeting

    @staticmethod
    def create_recurring_meeting(title: str, start_time, recurrence_pattern: str, host: User, **kwargs) -> Meeting:
        meeting = MeetingRepository.create_meeting({
            'title': title,
            'meeting_type': 'RECURRING',
            'start_time': start_time,
            'recurrence_pattern': recurrence_pattern,
            **kwargs
        }, host)
        try:
            WebhookService.notify_meeting_created(meeting)
        except Exception:
            pass
        return meeting

    @staticmethod
    def join_meeting_by_room_code(
        room_code: str,
        user: User | None = None,
        guest_name: str | None = None,
        password: str | None = None
    ) -> tuple[Meeting, MeetingParticipant]:
        meeting = MeetingRepository.get_meeting_by_room_code(room_code)
        if not meeting:
            raise ValueError("Meeting not found")

        if meeting.password and meeting.password != password:
            raise ValueError("Invalid meeting password")

        if meeting.status not in ['IN_PROGRESS', 'SCHEDULED']:
            raise ValueError("Meeting is not active")

        role = "HOST" if (user and meeting.host == user) else "PARTICIPANT"
        initial_status = "WAITING" if (meeting.enable_waiting_room and role != "HOST") else "JOINED"

        participant = MeetingParticipantRepository.add_participant(meeting, user, guest_name, role)
        participant.status = initial_status
        participant.save()

        if initial_status == "JOINED":
            try:
                WebhookService.notify_participant_joined(meeting, participant)
            except Exception:
                pass

        if meeting.status == 'SCHEDULED' and role == 'HOST':
            meeting.status = 'IN_PROGRESS'
            meeting.save()
            try:
                WebhookService.notify_meeting_started(meeting)
            except Exception:
                pass

        return meeting, participant

    @staticmethod
    def leave_meeting(participant: MeetingParticipant) -> None:
        participant.status = 'LEFT'
        participant.left_at = timezone.now()
        participant.save()

        try:
            WebhookService.notify_participant_left(participant.meeting, participant, reason="left")
        except Exception:
            pass

        meeting = participant.meeting
        has_joined = meeting.participants.filter(status='JOINED').exists()
        if participant.role == 'HOST' or (meeting.host == participant.user and not has_joined):
            meeting.status = 'COMPLETED'
            meeting.end_time = timezone.now()
            meeting.save()
            try:
                WebhookService.notify_meeting_ended(meeting)
            except Exception:
                pass

    @staticmethod
    def toggle_recording(meeting: Meeting) -> Meeting:
        meeting.is_recording = not meeting.is_recording
        meeting.save()
        return meeting


class MeetingParticipantService:
    @staticmethod
    def admit_from_waiting_room(participant: MeetingParticipant) -> None:
        participant.status = 'JOINED'
        participant.save()
        try:
            WebhookService.notify_participant_joined(participant.meeting, participant)
        except Exception:
            pass

    @staticmethod
    def remove_participant(participant: MeetingParticipant) -> None:
        try:
            WebhookService.notify_participant_left(participant.meeting, participant, reason="removed")
        except Exception:
            pass
        MeetingParticipantRepository.remove_participant(participant)

    @staticmethod
    def toggle_hand_raise(participant: MeetingParticipant) -> MeetingParticipant:
        participant.has_raised_hand = not participant.has_raised_hand
        if participant.has_raised_hand:
            participant.hand_raised_at = timezone.now()
        else:
            participant.hand_raised_at = None
        participant.save()
        return participant

    @staticmethod
    def toggle_audio(participant: MeetingParticipant) -> MeetingParticipant:
        participant.is_audio_on = not participant.is_audio_on
        participant.save()
        return participant

    @staticmethod
    def toggle_video(participant: MeetingParticipant) -> MeetingParticipant:
        participant.is_video_on = not participant.is_video_on
        participant.save()
        return participant

    @staticmethod
    def toggle_screen_share(participant: MeetingParticipant) -> MeetingParticipant:
        participant.is_screen_sharing = not participant.is_screen_sharing
        participant.save()
        return participant
