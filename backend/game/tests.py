from time import timezone
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone as django_timezone

from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

from game.models import Game, Leaderboard, PlayerProfile, Round
import datetime
import pytest

# Create your tests here.

User = get_user_model()

"""
Fixtures include:
user, superuser, clients, with respective permissions
player_profile with user permissions
game, round, leaderboard with mock data
"""


@pytest.fixture
def user(db):
    user = User.objects.create_user(
        username='user', password='testpassword123')
    return user


@pytest.fixture
def superuser(db):
    superuser = User.objects.create_superuser(
        username='superuser', password='testpassword123')
    return superuser


@pytest.fixture
def player_profile(user):
    player_profile = PlayerProfile.objects.get(pk=user.id)
    return player_profile


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_client(api_client, user):
    refresh = RefreshToken.for_user(user)
    api_client.cookies['AccessToken'] = str(refresh.access_token)
    api_client.cookies['PauseTime'] = str(django_timezone.now())
    api_client.credentials(HTTP_AUTHORIZATION=f'JWT {refresh.access_token}')
    return api_client


@pytest.fixture
def superuser_client(api_client, superuser):
    refresh = RefreshToken.for_user(superuser)
    api_client.credentials(HTTP_AUTHORIZATION=f'JWT {refresh.access_token}')
    return api_client


@pytest.fixture
def game(db, player_profile):
    new_game = Game.objects.create(
        id=1, player=player_profile, secret_number='1234', game_round=0, total_time=datetime.timedelta(seconds=0))
    return new_game


@pytest.fixture
def base_round(db, game):
    base_round = Round.objects.create(
        game=game, guess='1111', correct_numbers=1, correct_positions=1)
    return base_round


@pytest.fixture
def leaderboard(db, player_profile, game):
    leaderboard = Leaderboard.objects.create(
        result='W', total_time=datetime.timedelta(minutes=1, seconds=30), difficulty=4, player=player_profile, game=game)
    return leaderboard


@pytest.mark.django_db
class TestPlayerProfileViewSet:
    def test_get_player_with_user(self, user, player_profile, user_client):
        url = reverse('playerprofile-detail', args=[player_profile.player.id])
        response = user_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['player'] == user.id

    def test_get_player_list_with_superuser(self, superuser, superuser_client):
        url = reverse('playerprofile-list')

        response = superuser_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list) == True

    def test_get_player_list_with_user_unauthorized(self, user, user_client):
        url = reverse('playerprofile-list')

        response = user_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_player_list_with_user_invalid_token(self, user, player_profile, user_client):
        url = reverse('playerprofile-detail', args=[player_profile.player.id])
        user_client.credentials(HTTP_AUTHORIZATION=f'JWT {'bad token'}')
        response = user_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_player_after_user_created(self, user, user_client):
        url = f'{settings.BASE_URL}/auth/users/'
        credentials = {
            "username": 'testuser2',
            "password": 'testpassword123'
        }
        response = user_client.post(url, credentials, format='json')
        new_player = PlayerProfile.objects.filter(
            pk=response.data['id']).exists()
        assert response.status_code == status.HTTP_201_CREATED
        assert new_player == True

    def test_create_duplicate_player(self, user, user_client):
        url = f'{settings.BASE_URL}/auth/users/'
        credentials = {
            "username": 'user',
            "password": 'testpassword123'
        }
        response = user_client.post(url, credentials, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestDifficultyConfigView:
    def test_get_difficulty(self, player_profile, user_client):
        url = reverse('get-difficulty')
        response = user_client.get(url)
        difficulty = player_profile.difficulty

        assert response.status_code == status.HTTP_200_OK
        assert type(difficulty) == int
        assert difficulty == response.data

    def test_patch_difficulty(self, player_profile, user_client):
        url = reverse('get-difficulty')

        patch_data = {
            "difficulty": 5
        }

        response = user_client.patch(url, data=patch_data, format='json')
        player_profile.refresh_from_db()

        assert response.status_code == status.HTTP_200_OK
        assert response.data == patch_data['difficulty']
        assert player_profile.difficulty == patch_data['difficulty']


@pytest.mark.django_db
class TestNewGameView:
    def test_post_new_game(self, player_profile, user_client):
        url = reverse('new-game')

        response = user_client.post(url, format='json')
        player_profile.refresh_from_db()
        created_game = Game.objects.get(pk=player_profile.current_game.id)

        assert response.status_code == status.HTTP_201_CREATED
        assert player_profile.current_game == created_game
        assert created_game.player.id == player_profile.id
        assert created_game.secret_number == '1234'
        assert created_game.game_round == 0

    def test_post_new_game_unauthenticated(self, api_client):
        url = reverse('new-game')

        response = api_client.post(url, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestRoundsView:
    def test_get_rounds(self, base_round, user_client):
        url = reverse('game-rounds')
        response = user_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list) == True
        assert len(response.data) > 0

        round_data = response.data[0]

        assert round_data['game'] == 1
        assert round_data['guess'] == '1111'
        assert round_data['correct_numbers'] == 1
        assert round_data['correct_positions'] == 1

    def test_get_rounds_unauthorized(self, api_client):
        url = reverse('game-rounds')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_post_rounds(self, game, user_client):
        url = reverse('game-rounds')
        initial_game_round = game.game_round
        initial_game_time = game.total_time

        post_data = {
            "guess": '1234'
        }

        pre_post_leaderboard_entry = Leaderboard.objects.filter(
            game_id=game.id).exists()
        response = user_client.post(url, post_data, format='json')
        game.refresh_from_db()
        post_game_round = game.game_round
        post_game_time = game.total_time
        leaderboard_entry = Leaderboard.objects.filter(game_id=game.id).first()

        assert response.status_code == status.HTTP_201_CREATED
        # Test valid payload data
        assert response.data['game'] == 1
        assert response.data['guess'] == '1234'
        assert response.data['correct_numbers'] == 4
        assert response.data['correct_positions'] == 4

        # Test game data was updated
        assert initial_game_round == post_game_round - 1
        assert (initial_game_time < post_game_time) == True
        assert pre_post_leaderboard_entry == False
        assert leaderboard_entry.result == 'W'

        # Test updated game data type
        assert isinstance(game.total_time, datetime.timedelta) == True

    def test_post_rounds_unauthorized(self, api_client):
        url = reverse('game-rounds')
        response = api_client.post(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_post_rounds_invalid_data_type(self, game, user_client):
        url = reverse('game-rounds')
        post_data = {
            "guess": [1, 2, 3, 4]
        }

        response = user_client.post(url, post_data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_post_rounds_invalid_data_length(self, game, user_client):
        url = reverse('game-rounds')
        post_data = {
            "guess": '1234567'
        }

        response = user_client.post(url, post_data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_post_rounds_duplicate_guess(self, game, base_round, user_client):
        url = reverse('game-rounds')
        post_data = {
            "guess": '1111'
        }

        response = user_client.post(url, post_data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLeaderboardTotalsView:
    def test_get_totals(self, leaderboard, user_client):
        url = reverse('leaderboard')

        response = user_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['wins'] == 1
        assert response.data['fastest_time'] == datetime.timedelta(
            minutes=1, seconds=30)


@pytest.mark.django_db
class TestStartTimeView:
    def test_get_start_time(self, game, user_client):
        url = reverse('start-time')
        response = user_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(
            response.data['start_time'], datetime.datetime) == True


@pytest.mark.django_db
class TestResumeGameView:
    def test_patch_resume_game(self, game, user_client):
        url = reverse('resume-game')

        old_time = game.start_time
        response = user_client.patch(url)
        game.refresh_from_db()
        new_time = game.start_time

        assert response.status_code == status.HTTP_200_OK
        assert (new_time > old_time) == True

    def test_patch_resume_game_bad_token(self, game, user_client):
        url = reverse('resume-game')
        user_client.credentials(HTTP_AUTHORIZATION=f'JWT {'bad token'}')
        response = user_client.patch(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
class TestGameViewSet:
    def test_get_game_list_with_superuser(self, superuser, superuser_client):
        url = reverse('game-list')

        response = superuser_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list) == True

    def test_get_game_list_with_user(self, user, user_client):
        url = reverse('game-list')

        response = user_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestRoundViewSet:
    def test_get_round_list_with_superuser(self, superuser, superuser_client):
        url = reverse('round-list')

        response = superuser_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list) == True

    def test_get_round_list_with_user(self, user, user_client):
        url = reverse('round-list')

        response = user_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestLeaderboardViewSet:
    def test_get_leaderboard_list_with_superuser(self, superuser, superuser_client):
        url = reverse('leaderboard-list')

        response = superuser_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list) == True

    def test_get_leaderboard_list_with_user(self, user, user_client):
        url = reverse('leaderboard-list')

        response = user_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
