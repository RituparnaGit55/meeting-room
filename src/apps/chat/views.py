from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from apps.meetings.models import Meeting, MeetingParticipant
from .models import Message
from .serializers import MessageSerializer


def _get_user_meeting_ids(user):
    """Get meeting IDs where user is host or participant."""
    hosted = Meeting.objects.filter(host=user).values_list('id', flat=True)
    participated = MeetingParticipant.objects.filter(user=user).values_list('meeting_id', flat=True)
    return set(hosted) | set(participated)


class MessageListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def get_queryset(self):
        meeting_ids = _get_user_meeting_ids(self.request.user)
        return Message.objects.filter(meeting_id__in=meeting_ids)


class MessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def get_queryset(self):
        meeting_ids = _get_user_meeting_ids(self.request.user)
        return Message.objects.filter(meeting_id__in=meeting_ids)


class MessageFileUploadView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        meeting_ids = _get_user_meeting_ids(self.request.user)
        return Message.objects.filter(meeting_id__in=meeting_ids)
