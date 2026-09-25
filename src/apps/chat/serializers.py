from rest_framework import serializers
from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"

    def validate(self, attrs):
        meeting = attrs.get('meeting')
        content = attrs.get('content')
        if meeting and content:
            from apps.meetings.services import check_text_against_meeting_keywords
            is_restricted, _ = check_text_against_meeting_keywords(meeting.id, content)
            if is_restricted:
                raise serializers.ValidationError({
                    "content": "This message contains a restricted keyword or phrase that is not allowed in this meeting."
                })
        return attrs

