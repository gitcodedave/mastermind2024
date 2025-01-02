import requests
from django.conf import settings

class PlayerDataMixin:
    def get_player_data(self, request):   
            token = request.COOKIES.get('AccessToken')
            response = requests.get(f'{settings.BASE_URL}/game/playerprofiles/me', headers={
                "Authorization": f'JWT {token}'
            })
            if response.status_code != 200:
                response.raise_for_status()
            return response.json()