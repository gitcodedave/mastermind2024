from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.


class PlayerProfile(models.Model):
    """
    Represents a user with added fields: 
    difficulty - How many numbers the need to guess 
    current game - id for retrieving their current game state
    """
    difficulty = models.IntegerField(
        validators=[MinValueValidator(4), MaxValueValidator(6)], default=4)
    player = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    current_game = models.ForeignKey(
        'Game', on_delete=models.CASCADE, related_name='game_players', blank=True, null=True)

    def __str__(self):
        return f'{self.player.username}'


class Game(models.Model):
    """
    Represents the game config
    player - id of who the game belongs to
    """
    player = models.ForeignKey(
        PlayerProfile, on_delete=models.CASCADE, related_name='active_player_games')
    secret_number = models.CharField(max_length=6)
    game_round = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)], default=0)
    start_time = models.DateTimeField(default=timezone.now)
    total_time = models.DurationField(blank=True, null=True)

    def __str__(self):
        return f'Game ID: {self.id}'


class Round(models.Model):
    """
    Represents each time a player makes a guess
    game - id of the game that the rounds belong to
    """
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
            models.UniqueConstraint(
                fields=['game', 'guess'], name='unique_guess')
        ]


class Leaderboard(models.Model):
    """
    Represents the results of a player's wins, includes time of game and difficulty
    """
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
        constraints = [
            models.UniqueConstraint(
                fields=['player', 'game'], name='unique_player_game')
        ]
