from django.utils.timesince import timesince
from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    meeting_title = serializers.SerializerMethodField()
    type_display = serializers.SerializerMethodField()
    time_ago = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "id",
            "user",
            "meeting",
            "meeting_title",
            "type",
            "type_display",
            "title",
            "message",
            "is_read",
            "created_at",
            "time_ago",
        ]
        read_only_fields = ["id", "user", "type", "title", "message", "created_at"]

    def get_meeting_title(self, obj):
        if obj.meeting:
            return obj.meeting.title
        return None

    def get_type_display(self, obj):
        return obj.get_type_display()

    def get_time_ago(self, obj):
        return timesince(obj.created_at) + " ago"
