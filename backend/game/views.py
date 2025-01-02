from django.utils import timezone as django_timezone

from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .mixins import PlayerDataMixin
from .models import Game, PlayerProfile, Round
from .permissions import IsSuperUser
from .serializers import GameSerializer, PlayerProfileSerializer, RoundSerializer
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
        return [permission() for permission in permission_classes]

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


class RoundsView(PlayerDataMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        player_data = self.get_player_data(request)

        game_id = player_data.get('current_game')

        if game_id is None:
            return Response({'error': 'Game not found'}, status=status.HTTP_404_NOT_FOUND)

        round_data = Round.objects.filter(
            game_id=game_id).order_by('timestamp')
        serializer = RoundSerializer(round_data, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        player_data = self.get_player_data(request)
        game_id = player_data.get('current_game')
        game = Game.objects.get(pk=game_id)

        secret_number = game.secret_number
        secret_number_list = [x for x in secret_number]

        guess = request.data.get('guess')
        guess_list = [x for x in guess]

        correct_numbers, correct_positions = self.evaluate_guesses(
            secret_number_list=secret_number_list, guess_list=guess_list)
        
        round_data = {
            "game": game_id,
            "guess": guess, 
            "correct_numbers": correct_numbers,
            "correct_positions": correct_positions
        }

        serializer = RoundSerializer(data=round_data)
        serializer.is_valid()
        serializer.save()

        current_time = django_timezone.now()
        total_time = current_time - game.created_at

        game.game_round += 1
        game.total_time = total_time
        game.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
        

    def evaluate_guesses(self, secret_number_list, guess_list):
        correct_numbers = 0
        correct_positions = 0

        for index, num in enumerate(guess_list):
            if secret_number_list[index] == num:
                correct_numbers += 1
                correct_positions += 1
                guess_list[index] = 'x'
                secret_number_list[index] = 'x'

        for index, num in enumerate(guess_list):
            if num == 'x':
                continue
            if num in secret_number_list:
                correct_numbers += 1
                new_index = secret_number_list.index(num)
                secret_number_list[new_index] = 'x'

        return correct_numbers, correct_positions