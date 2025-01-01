from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.


class PlayerProfile(models.Model):
    difficulty = models.IntegerField(
        validators=[MinValueValidator(4), MaxValueValidator(6)], default=4)
    player = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    current_game = models.ForeignKey(
        'Game', on_delete=models.CASCADE, related_name='game_players', blank=True, null=True)


class Game(models.Model):
    active_player = models.ForeignKey(
        PlayerProfile, on_delete=models.CASCADE, related_name='active_player_games')
    secret_number = models.CharField(max_length=6)
    game_round = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)], default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    total_time = models.DurationField(blank=True, null=True)


class Round(models.Model):
    game = models.ForeignKey(
        Game, on_delete=models.CASCADE, related_name='rounds')
    guess = models.CharField(max_length=6)
    correct_numbers = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(6)])
    correct_positions = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(6)])
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraints(
                fields=['game', 'guess'], name='unique_guess')
        ]


class Leaderboard(models.Model):
    RESULT_WIN = 'W'
    RESULT_LOSS = 'L'
    RESULT_CHOICES = [
        (RESULT_WIN, 'Win'),
        (RESULT_LOSS, 'Loss')
    ]
    result = models.CharField(max_length=1, choices=RESULT_CHOICES)
    total_time = models.DurationField()
    difficulty = models.IntegerField(
        validators=[MinValueValidator(4), MaxValueValidator(6)])
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constrains = [
            models.UniqueConstraint(
                fields=['player', 'game'], name='unique_player_game')
        ]
