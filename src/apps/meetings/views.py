from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from .models import Meeting, MeetingParticipant
from .serializers import (
    MeetingSerializer, CreateMeetingSerializer,
    MeetingParticipantSerializer, JoinMeetingSerializer
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
        if meeting_type == 'INSTANT':
            meeting = MeetingService.create_instant_meeting(
                title=data.pop('title'),
                host=self.request.user,
                **data
            )
        else:
            meeting = MeetingService.create_scheduled_meeting(
                title=data.pop('title'),
                start_time=data.pop('start_time'),
                host=self.request.user,
                **data
            )
        MeetingParticipantRepository.add_participant(
            meeting, self.request.user, role='HOST'
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


class JoinMeetingAPIView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = JoinMeetingSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            room_code = serializer.validated_data.get('room_code')
            meeting_id = serializer.validated_data.get('meeting_id')
            if not room_code and not meeting_id:
                return Response({"error": "Room code or meeting ID required"}, status=status.HTTP_400_BAD_REQUEST)
            
            if meeting_id:
                meeting = MeetingRepository.get_meeting_by_meeting_id(meeting_id)
                if not meeting:
                    raise ValueError("Meeting not found")
                room_code = meeting.room_code

            meeting, participant = MeetingService.join_meeting_by_room_code(
                room_code,
                user=request.user if request.user.is_authenticated else None,
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
class MeetingDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'meetings/dashboard.html'


class CreateMeetingView(LoginRequiredMixin, TemplateView):
    template_name = 'meetings/create.html'


class MeetingRoomView(TemplateView):
    template_name = 'meetings/room.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room_code = kwargs.get('room_code', '')
        context['room_code'] = room_code
        
        # Auto add authenticated user as participant if not already added
        if self.request.user.is_authenticated:
            try:
                from .models import Meeting
                meeting = MeetingRepository.get_meeting_by_room_code(room_code)
                if meeting:
                    # Check if already participant
                    participant_exists = MeetingParticipant.objects.filter(
                        meeting=meeting, user=self.request.user
                    ).exists()
                    if not participant_exists:
                        MeetingParticipantRepository.add_participant(
                            meeting, self.request.user, role='PARTICIPANT'
                        )
            except Exception:
                pass  # Just ignore errors, page will still load
                
        return context


class JoinMeetingPageView(TemplateView):
    template_name = 'meetings/join.html'


class MyMeetingsView(LoginRequiredMixin, TemplateView):
    template_name = 'meetings/my_meetings.html'
