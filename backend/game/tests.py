from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from game.models import Game, PlayerProfile, Round
from rest_framework_simplejwt.tokens import RefreshToken
import pytest

# Create your tests here.

User = get_user_model()

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
        id=1, active_player=player_profile, secret_number='1234', game_round=0)
    return new_game

@pytest.fixture
def base_round(db, game):
    base_round = Round.objects.create(
        game=game, guess='1234', correct_numbers=4, correct_positions=4)
    return base_round


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
    
    def test_get_player_list_with_user(self, user, user_client):
        url = reverse('playerprofile-list')
        
        response = user_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
