from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import APIKey
from .serializers import APIKeySerializer


class APIKeyListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = APIKeySerializer
    queryset = APIKey.objects.all()


class APIKeyDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = APIKeySerializer
    queryset = APIKey.objects.all()
