from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Summary
from .serializers import SummarySerializer


class SummaryListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SummarySerializer
    queryset = Summary.objects.all()


class SummaryDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SummarySerializer
    queryset = Summary.objects.all()
