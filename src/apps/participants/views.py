from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Participant
from .serializers import ParticipantSerializer


class ParticipantListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ParticipantSerializer
    queryset = Participant.objects.all()


class ParticipantDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ParticipantSerializer
    queryset = Participant.objects.all()
