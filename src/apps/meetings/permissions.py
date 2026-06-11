
from rest_framework.permissions import BasePermission
from apps.meetings.models import Meeting, MeetingParticipant


class IsMeetingHost(BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Meeting):
            return obj.host == request.user
        if isinstance(obj, MeetingParticipant):
            return obj.meeting.host == request.user
        return False


class IsMeetingHostOrCoHost(BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Meeting):
            return obj.host == request.user
        if isinstance(obj, MeetingParticipant):
            if obj.meeting.host == request.user:
                return True
            try:
                participant = MeetingParticipant.objects.get(meeting=obj.meeting, user=request.user)
                return participant.role in ['HOST', 'CO_HOST']
            except MeetingParticipant.DoesNotExist:
                return False
        return False


class IsMeetingParticipant(BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Meeting):
            return obj.host == request.user or obj.participants.filter(user=request.user, status__in=['JOINED', 'WAITING']).exists()
        if isinstance(obj, MeetingParticipant):
            return obj.user == request.user or obj.meeting.host == request.user
        return False
