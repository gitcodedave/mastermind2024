from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from backend.game.models import PlayerProfile
from backend.game.permissions import IsSuperUser
from backend.game.serializers import PlayerProfileSerializer
# Create your views here.

class PlayerProfileViewSet(ModelViewSet):
    queryset = PlayerProfile.objects.all()
    serializer_class = PlayerProfileSerializer

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [IsSuperUser]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]
        return[permission() for permission in permission_classes]

    @action(detail=False, methods=['GET'])
    def me(self, request):
        player = PlayerProfile.objects.get(player_id=request.user.id)
        if request.method == 'GET':
            serializer = PlayerProfileSerializer(player)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
