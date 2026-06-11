from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Recording
from .serializers import RecordingSerializer


class RecordingListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RecordingSerializer
    queryset = Recording.objects.all()


class RecordingDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RecordingSerializer
    queryset = Recording.objects.all()
