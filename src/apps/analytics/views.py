from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import MeetingAnalytics, UserAnalytics
from .serializers import MeetingAnalyticsSerializer, UserAnalyticsSerializer


class MeetingAnalyticsListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MeetingAnalyticsSerializer
    queryset = MeetingAnalytics.objects.all()


class MeetingAnalyticsDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MeetingAnalyticsSerializer
    queryset = MeetingAnalytics.objects.all()


class UserAnalyticsListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserAnalyticsSerializer
    queryset = UserAnalytics.objects.all()


class UserAnalyticsDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserAnalyticsSerializer
    queryset = UserAnalytics.objects.all()
