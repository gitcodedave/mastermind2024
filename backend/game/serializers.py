from rest_framework import serializers
from .models import PlayerProfile, Game, Round, Leaderboard


class PlayerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerProfile
        fields = ['player', 'difficulty', 'current_game']


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['id', 'active_player', 'secret_number',
                  'game_round', 'created_at', 'total_time']


class RoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Round
        fields = ['id', 'game', 'guess', 'correct_numbers',
                  'correct_positions', 'timestamp']


class LeaderboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leaderboard
        fields = ['id', 'result', 'total_time', 'difficulty', 'player', 'game']
