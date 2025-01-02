from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .mixins import PlayerDataMixin
from .models import PlayerProfile
from .permissions import IsSuperUser
from .serializers import GameSerializer, PlayerProfileSerializer
import requests
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
        

class NewGameView(PlayerDataMixin, APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            player_data = self.get_player_data(request)
            difficulty = player_data.get('difficulty')

            new_game_data = {
                "player": player_data['player'],
                "secret_number": self.generate_random_number(difficulty=difficulty),
                "game_round": 0
            }

            serializer = GameSerializer(data=new_game_data)
            serializer.is_valid(raise_exception=True)
            game = serializer.save()

            active_player = PlayerProfile.objects.get(
                player=player_data['player']
            )
            active_player.current_game = game
            active_player.save()

            return Response({}, status=status.HTTP_201_CREATED)
        except requests.exceptions.RequestException as error:
            return Response({'error': f'Error with external API: {str(error)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def generate_random_number(self, difficulty):
        url = f'https://www.random.org/integers/?num={
            difficulty}&min=0&max=7&col=1&base=10&format=plain&rnd=new'
        response = requests.get(url)
        if response.status_code != 200:
            response.raise_for_status()

        secret_number = response.text
        return secret_number