from typing import cast, Any
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import SessionAuthentication
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from apps.accounts.models import User
from .models import Meeting, MeetingParticipant, MeetingRecording
from .serializers import (
    MeetingSerializer, CreateMeetingSerializer,
    MeetingParticipantSerializer, JoinMeetingSerializer,
    MeetingRecordingSerializer
)
from .services.meeting_service import MeetingService, MeetingParticipantService
from .repositories.meeting_repository import MeetingRepository, MeetingParticipantRepository
from .permissions import IsMeetingHost, IsMeetingParticipant


class MeetingViewSet(viewsets.ModelViewSet):
    queryset = Meeting.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = None  # Disable pagination for this viewset

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateMeetingSerializer
        return MeetingSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsMeetingHost()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        return Meeting.objects.filter(host=user) | Meeting.objects.filter(participants__user=user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        meeting = self.perform_create(serializer)
        # Use full MeetingSerializer to get room_code etc.
        full_serializer = MeetingSerializer(meeting, context={'request': request})
        headers = self.get_success_headers(full_serializer.data)
        return Response(full_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        meeting_type = serializer.validated_data.get('meeting_type', 'SCHEDULED')
        data = serializer.validated_data.copy()
        user = cast(User, self.request.user)
        if meeting_type in ['INSTANT', 'LINK_GENERATION', 'ID_GENERATION']:
            meeting = MeetingService.create_instant_meeting(
                title=data.pop('title'),
                host=user,
                **data
            )
        else:
            meeting = MeetingService.create_scheduled_meeting(
                title=data.pop('title'),
                start_time=data.pop('start_time'),
                host=user,
                **data
            )
        MeetingParticipantRepository.add_participant(
            meeting, user, role='HOST'
        )
        return meeting

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        meeting = self.get_object()
        try:
            _, participant = MeetingService.join_meeting_by_room_code(
                room_code=meeting.room_code,
                user=request.user,
                password=request.data.get('password')
            )
            return Response(MeetingParticipantSerializer(participant).data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        meeting = self.get_object()
        participant = get_object_or_404(MeetingParticipant, meeting=meeting, user=request.user)
        MeetingService.leave_meeting(participant)
        return Response({"message": "Successfully left meeting"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsMeetingHost])
    def toggle_recording(self, request, pk=None):
        meeting = self.get_object()
        meeting = MeetingService.toggle_recording(meeting)
        return Response(MeetingSerializer(meeting, context={'request': request}).data)


class MeetingParticipantViewSet(viewsets.ModelViewSet):
    queryset = MeetingParticipant.objects.all()
    permission_classes = [IsAuthenticated, IsMeetingParticipant]
    serializer_class = MeetingParticipantSerializer

    def get_queryset(self):
        meeting_id = self.kwargs.get('meeting_pk')
        if meeting_id:
            return MeetingParticipant.objects.filter(meeting_id=meeting_id)
        return self.queryset.none()

    @action(detail=True, methods=['post'], permission_classes=[IsMeetingHost])
    def admit(self, request, pk=None):
        participant = self.get_object()
        MeetingParticipantService.admit_from_waiting_room(participant)
        return Response({"message": "Participant admitted"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsMeetingHost])
    def remove(self, request, pk=None):
        participant = self.get_object()
        MeetingParticipantService.remove_participant(participant)
        return Response({"message": "Participant removed"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def toggle_hand(self, request, pk=None):
        participant = self.get_object()
        participant = MeetingParticipantService.toggle_hand_raise(participant)
        return Response(MeetingParticipantSerializer(participant).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def toggle_audio(self, request, pk=None):
        participant = self.get_object()
        participant = MeetingParticipantService.toggle_audio(participant)
        return Response(MeetingParticipantSerializer(participant).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def toggle_video(self, request, pk=None):
        participant = self.get_object()
        participant = MeetingParticipantService.toggle_video(participant)
        return Response(MeetingParticipantSerializer(participant).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def toggle_screen(self, request, pk=None):
        participant = self.get_object()
        participant = MeetingParticipantService.toggle_screen_share(participant)
        return Response(MeetingParticipantSerializer(participant).data, status=status.HTTP_200_OK)


from rest_framework.parsers import MultiPartParser, FormParser

class UploadRecordingView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MeetingRecordingSerializer
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        request = cast(Any, self.request)
        meeting_id = request.data.get('meeting')
        meeting = get_object_or_404(Meeting, pk=meeting_id)
        user = cast(User, self.request.user)
        # Verify user is host or participant
        if meeting.host != user and not MeetingParticipant.objects.filter(meeting=meeting, user=user).exists():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You must be a participant to upload a recording.")
            
        file_obj = request.data.get('file')
        file_size = file_obj.size if file_obj else 0
        
        serializer.save(
            started_by=user,
            file_size=file_size
        )


class JoinMeetingAPIView(generics.GenericAPIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]
    serializer_class = JoinMeetingSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            room_code = serializer.validated_data.get('room_code')
            meeting_id = serializer.validated_data.get('meeting_id')
            
            identifier = room_code or meeting_id
            if not identifier:
                return Response({"error": "Room code or meeting ID required"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Try to resolve by room code first (case-insensitive)
            meeting = MeetingRepository.get_meeting_by_room_code(identifier)
            if not meeting:
                # Try to resolve by meeting ID
                meeting = MeetingRepository.get_meeting_by_meeting_id(identifier)
            
            if not meeting:
                raise ValueError("Meeting not found")
            
            room_code = meeting.room_code

            meeting, participant = MeetingService.join_meeting_by_room_code(
                room_code,
                user=cast(Any, request.user if request.user.is_authenticated else None),
                guest_name=serializer.validated_data.get('guest_name'),
                password=serializer.validated_data.get('password')
            )
            return Response({
                "meeting": MeetingSerializer(meeting, context={'request': request}).data,
                "participant": MeetingParticipantSerializer(participant).data
            }, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Web Views
class MeetingDashboardView(TemplateView):
    template_name = 'meetings/dashboard.html'


class CreateMeetingView(LoginRequiredMixin, TemplateView):
    template_name = 'meetings/create.html'


class MeetingRoomView(TemplateView):
    template_name = 'meetings/room.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room_code = kwargs.get('room_code', '')
        meeting = None
        try:
            meeting = MeetingRepository.get_meeting_by_room_code(room_code)
            if meeting:
                context['meeting_id'] = meeting.meeting_id
                context['meeting_pk'] = meeting.id
        except Exception:
            pass

        context['room_code'] = room_code
        
        participant = None
        # Auto add authenticated user as participant if not already added
        if self.request.user.is_authenticated:
            try:
                if meeting:
                    user = cast(User, self.request.user)
                    # Check if already participant
                    participant = MeetingParticipant.objects.filter(
                        meeting=meeting, user=user
                    ).first()
                    if not participant:
                        participant = MeetingParticipantRepository.add_participant(
                            meeting, user, role='PARTICIPANT'
                        )
            except Exception:
                pass  # Just ignore errors, page will still load
                
        if participant:
            context['participant_id'] = participant.id
            context['participant_role'] = participant.role
            context['is_host'] = (participant.role == 'HOST')
            context['participant_name'] = participant.user.first_name or participant.user.email if participant.user else participant.guest_name
            context['participant_status'] = participant.status
        else:
            # Maybe a guest
            context['participant_id'] = None
            context['participant_role'] = 'GUEST'
            context['is_host'] = False
            context['participant_name'] = 'Guest'
            context['participant_status'] = 'JOINED'
            
        context['enable_waiting_room'] = meeting.enable_waiting_room if meeting else False
        
        # Pass existing participants
        if meeting:
            if context.get('is_host'):
                context['participants'] = MeetingParticipant.objects.filter(meeting=meeting).exclude(status__in=['LEFT', 'REMOVED'])
            else:
                context['participants'] = MeetingParticipant.objects.filter(meeting=meeting, status='JOINED')
        else:
            context['participants'] = []
            
        return context


class JoinMeetingPageView(TemplateView):
    template_name = 'meetings/join.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['room_code'] = kwargs.get('room_code', '')
        return context


class MyMeetingsView(LoginRequiredMixin, TemplateView):
    template_name = 'meetings/my_meetings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        meetings = Meeting.objects.filter(host=user) | Meeting.objects.filter(participants__user=user)
        context['recordings'] = MeetingRecording.objects.filter(meeting__in=meetings).distinct().order_by('-created_at')
        return context
