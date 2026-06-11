from rest_framework import serializers
from .models import MeetingAnalytics, UserAnalytics


class MeetingAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingAnalytics
        fields = "__all__"


class UserAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnalytics
        fields = "__all__"
