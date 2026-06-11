from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Transcript
from .serializers import TranscriptSerializer


class TranscriptListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TranscriptSerializer
    queryset = Transcript.objects.all()


class TranscriptDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TranscriptSerializer
    queryset = Transcript.objects.all()
