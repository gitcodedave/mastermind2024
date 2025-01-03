from django.conf import settings
from django.utils import timezone as django_timezone

from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .mixins import PlayerDataMixin
from .permissions import IsSuperUser
from .models import Game, Leaderboard, PlayerProfile, Round
from .serializers import GameSerializer, LeaderboardSerializer, PlayerProfileSerializer, RoundSerializer
import requests
import logging
logger = logging.getLogger(__name__)

# Create your views here.


class PlayerProfileViewSet(ModelViewSet):
    """
    Endpoint: playerprofiles/
    Retrieves list of all Players, requires IsSuperUser permission
    POST, PATCH, DELETE, require IsAuthenticated permission
    """
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
        """
         Custom action endpoint: auth/users/me/ 
         Retrieves Player's data using access token in cookies
        """
        player = PlayerProfile.objects.get(player_id=request.user.id)
        if request.method == 'GET':
            serializer = PlayerProfileSerializer(player)
            return Response(serializer.data, status=status.HTTP_200_OK)


class DifficultyConfigView(PlayerDataMixin, APIView):
    """
    Endpoint: difficulty/
    Handles GET request - retrieves Player's difficulty setting
    Handles PATCH request - updates Player's difficulty setting
    """
    def get(self, request):
        player_data = self.get_player_data(request)

        difficulty = player_data.get('difficulty')

        return Response(difficulty, status=status.HTTP_200_OK)

    def patch(self, request):
        player_data = self.get_player_data(request)

        difficulty = int(request.data.get('difficulty'))

        player = PlayerProfile.objects.get(player=player_data.get('player'))

        player.difficulty = difficulty
        player.save()
        logger.debug('Difficulty changed to: %s', difficulty)
        return Response(difficulty, status=status.HTTP_200_OK)


class NewGameView(PlayerDataMixin, APIView):
    """
    Endpoint: newgame/
    Handles POST request - creates Game entry using external API data
    Updates Player's current_game id
    """
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
            logger.debug('New game created with difficulty: %s', difficulty)

            active_player = PlayerProfile.objects.get(
                player=player_data['player']
            )
            active_player.current_game = game
            active_player.save()
            logger.debug('current_game updated as: %s', game)

            return Response({}, status=status.HTTP_201_CREATED)
        except requests.exceptions.RequestException as error:
            return Response({'error': f'Error with external API: {str(error)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def generate_random_number(self, difficulty):
        """
        Helper function - uses external API to generate random number
        """
        if not settings.TESTING:
            url = f'https://www.random.org/integers/?num={
                difficulty}&min=0&max=7&col=1&base=10&format=plain&rnd=new'
            response = requests.get(url)
            if response.status_code != 200:
                response.raise_for_status()

            secret_number = response.text
            return secret_number
        else:
            return '1234'


class RoundsView(PlayerDataMixin, APIView):
    """
    Endpoint: gamerounds/
    Handles GET request - retrieves Player's round-data from current game
    Handles POST request - creates Round entry using Player's guess
    """
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
        """
        Two entries may be created from this:
        1. A Round entry
        2. If the Player guesses correctly, a Leaderboard entry is created
        """
        player_data = self.get_player_data(request)
        game_id = player_data.get('current_game')
        game = Game.objects.get(pk=game_id)

        secret_number = game.secret_number
        secret_number_list = [x for x in secret_number]

        guess = request.data.get('guess')
        logger.debug('Guess made: %s', guess)

        guess_list = [x for x in guess]
        if len(guess_list) > 6:
            return Response({'error': 'Guess length too long'}, status=status.HTTP_400_BAD_REQUEST)

        correct_numbers, correct_positions = self.evaluate_guesses(
            secret_number_list=secret_number_list, guess_list=guess_list)

        round_data = {
            "game": game_id,
            "guess": guess,
            "correct_numbers": correct_numbers,
            "correct_positions": correct_positions
        }

        serializer = RoundSerializer(data=round_data)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response({'error': 'Wrong data type'}, status=status.HTTP_400_BAD_REQUEST)

        current_time = django_timezone.now()
        total_time = current_time - game.created_at

        game.game_round += 1
        game.total_time = total_time
        game.save()

        player = player_data.get('player')
        difficulty = player_data.get('difficulty')

        if correct_positions == difficulty:
            self.update_leaderboard(
                game=game, result='W', player=player, difficulty=difficulty)
        elif game.game_round >= 10:
            self.update_leaderboard(
                game=game, result='L', player=player, difficulty=difficulty)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def evaluate_guesses(self, secret_number_list, guess_list):
        """
        Helper function - compares Player's guess with secret_number
        """
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
    
    def update_leaderboard(self, game, result, player, difficulty):
        """
        Helper function - Creates new Leaderboard entry when player wins
        """
        leaderboard_data = {
            "result": result,
            "total_time": game.total_time,
            "difficulty": difficulty,
            "player": player,
            "game": game.id
        }

        serializer = LeaderboardSerializer(data=leaderboard_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.debug('Leaderboard win added for player id: %s', player)


class LeaderboardTotalsView(PlayerDataMixin, APIView):
    """
    Endpoint: leaderboard/
    Handles GET request - retrieves Player's win and fastest time stats
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        player_data = self.get_player_data(request)

        player = player_data.get('player')
        difficulty = player_data.get('difficulty')

        win_total = Leaderboard.objects.filter(
            player_id=player, result='W', difficulty=difficulty).count()
        fastest_game = Leaderboard.objects.filter(
            player_id=player, result='W', difficulty=difficulty).order_by('total_time').first()

        if not fastest_game:
            fastest_time = None
        else:
            fastest_time = fastest_game.total_time

        game_id = player_data.get('current_game')

        if game_id is None:
            return Response({'error': 'Game not found'}, status=status.HTTP_404_NOT_FOUND)

        rankings = {
            "wins": win_total,
            "fastest_time": fastest_time,
        }
        return Response(rankings, status=status.HTTP_200_OK)


class GameViewSet(ModelViewSet):
    """
    SuperUser only view - work with Game data
    Handles LIST, GET, POST, PATCH, DELETE
    """
    permission_classes = [IsSuperUser]
    queryset = Game.objects.all()
    serializer_class = GameSerializer


class RoundViewSet(ModelViewSet):
    """
    SuperUser only view - work with Round data
    Handles LIST, GET, POST, PATCH, DELETE
    """
    permission_classes = [IsSuperUser]
    queryset = Round.objects.all()
    serializer_class = RoundSerializer


class LeaderboardViewSet(ModelViewSet):
    """
    SuperUser only view - work with Leaderboard data
    Handles LIST, GET, POST, PATCH, DELETE
    """
    permission_classes = [IsSuperUser]
    queryset = Leaderboard.objects.all()
    serializer_class = LeaderboardSerializer
