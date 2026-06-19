from rest_framework import serializers
from django.utils import timezone
from apps.accounts.models import User
from apps.accounts.serializers import UserSerializer
from .models import Meeting, MeetingParticipant, MeetingRecording


class MeetingParticipantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = MeetingParticipant
        fields = '__all__'
        read_only_fields = ['joined_at', 'left_at']


class MeetingSerializer(serializers.ModelSerializer):
    host = UserSerializer(read_only=True)
    participants = MeetingParticipantSerializer(many=True, read_only=True)
    join_url = serializers.SerializerMethodField()

    class Meta:
        model = Meeting
        fields = '__all__'
        read_only_fields = ['room_code', 'meeting_id', 'created_at', 'updated_at', 'status']

    def get_join_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/meetings/join/{obj.room_code}/')
        return ''


class CreateMeetingSerializer(serializers.ModelSerializer):
    start_time = serializers.DateTimeField(required=False, allow_null=True)

    class Meta:
        model = Meeting
        fields = ['title', 'description', 'meeting_type', 'start_time', 'duration', 'password', 'enable_waiting_room', 'recurrence_pattern', 'recurrence_end_date']

    def validate(self, attrs):
        if attrs.get('meeting_type') in ['INSTANT', 'LINK_GENERATION', 'ID_GENERATION']:
            attrs['start_time'] = timezone.now()
        else:
            if 'start_time' not in attrs or attrs['start_time'] is None:
                raise serializers.ValidationError({'start_time': 'Start time is required for scheduled meetings'})
            if attrs['start_time'] < timezone.now():
                raise serializers.ValidationError({'start_time': 'Start time cannot be in the past'})
        return attrs


class JoinMeetingSerializer(serializers.Serializer):
    room_code = serializers.CharField(required=False)
    meeting_id = serializers.CharField(required=False)
    password = serializers.CharField(required=False, allow_blank=True)
    guest_name = serializers.CharField(required=False, allow_blank=True)


class MeetingRecordingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingRecording
        fields = '__all__'
