
from typing import Optional, List
from django.utils import timezone
from apps.accounts.models import User
from apps.meetings.models import Meeting, MeetingParticipant


class MeetingRepository:
    @staticmethod
    def create_meeting(data: dict, host: User) -> Meeting:
        meeting = Meeting.objects.create(
            title=data.get('title'),
            description=data.get('description', ''),
            meeting_type=data.get('meeting_type', 'SCHEDULED'),
            host=host,
            password=data.get('password'),
            start_time=data.get('start_time'),
            duration=data.get('duration', 60),
            enable_waiting_room=data.get('enable_waiting_room', False),
            recurrence_pattern=data.get('recurrence_pattern', 'NONE'),
            recurrence_end_date=data.get('recurrence_end_date'),
            status=data.get('status', 'SCHEDULED')
        )
        return meeting

    @staticmethod
    def get_meeting_by_id(meeting_id: int) -> Optional[Meeting]:
        try:
            return Meeting.objects.get(id=meeting_id)
        except Meeting.DoesNotExist:
            return None

    @staticmethod
    def get_meeting_by_room_code(room_code: str) -> Optional[Meeting]:
        try:
            return Meeting.objects.get(room_code=room_code.upper())
        except Meeting.DoesNotExist:
            return None

    @staticmethod
    def get_meeting_by_meeting_id(meeting_id_str: str) -> Optional[Meeting]:
        try:
            return Meeting.objects.get(meeting_id=meeting_id_str)
        except Meeting.DoesNotExist:
            return None

    @staticmethod
    def get_user_meetings(user: User) -> List[Meeting]:
        return Meeting.objects.filter(host=user) | Meeting.objects.filter(participants__user=user)

    @staticmethod
    def update_meeting(meeting: Meeting, data: dict) -> Meeting:
        for key, value in data.items():
            setattr(meeting, key, value)
        meeting.save()
        return meeting

    @staticmethod
    def delete_meeting(meeting: Meeting) -> None:
        meeting.delete()


class MeetingParticipantRepository:
    @staticmethod
    def add_participant(
        meeting: Meeting,
        user: Optional[User] = None,
        guest_name: Optional[str] = None,
        role: str = "PARTICIPANT"
    ) -> MeetingParticipant:
        if user:
            participant, _ = MeetingParticipant.objects.update_or_create(
                meeting=meeting,
                user=user,
                defaults={'role': role, 'status': 'JOINED'}
            )
        else:
            participant = MeetingParticipant.objects.create(
                meeting=meeting,
                guest_name=guest_name,
                role=role,
                status='JOINED'
            )
        return participant

    @staticmethod
    def get_participant_by_id(participant_id: int) -> Optional[MeetingParticipant]:
        try:
            return MeetingParticipant.objects.get(id=participant_id)
        except MeetingParticipant.DoesNotExist:
            return None

    @staticmethod
    def get_meeting_participants(meeting: Meeting) -> List[MeetingParticipant]:
        return MeetingParticipant.objects.filter(meeting=meeting, status__in=['WAITING', 'JOINED'])

    @staticmethod
    def update_participant(participant: MeetingParticipant, data: dict) -> MeetingParticipant:
        for key, value in data.items():
            setattr(participant, key, value)
        if 'has_raised_hand' in data:
            if data['has_raised_hand']:
                participant.hand_raised_at = timezone.now()
            else:
                participant.hand_raised_at = None
        participant.save()
        return participant

    @staticmethod
    def remove_participant(participant: MeetingParticipant) -> None:
        participant.status = 'REMOVED'
        participant.left_at = timezone.now()
        participant.save()
