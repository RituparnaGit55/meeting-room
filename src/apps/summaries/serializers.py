from rest_framework import serializers
from .models import Summary, MeetingNote


class SummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Summary
        fields = "__all__"


class MeetingNoteSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = MeetingNote
        fields = "__all__"
        read_only_fields = ["author", "created_at"]

    def get_author_name(self, obj):
        if obj.author:
            name = obj.author.get_full_name()
            return name if name.strip() else obj.author.email
        return "Anonymous"
