import requests
from django.conf import settings

class PlayerDataMixin:
    """
    Custom mixin - returns player data by using Access Token in cookies
    """
    def get_player_data(self, request):   
            token = request.COOKIES.get('AccessToken')
            response = requests.get(f'{settings.BASE_URL}/game/playerprofiles/me', headers={
                "Authorization": f'JWT {token}'
            })
            if response.status_code != 200:
                response.raise_for_status()
            return response.json()