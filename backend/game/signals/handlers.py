from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from game.models import PlayerProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_player_profile(sender, instance, created, **kwargs):
    """
    Uses the save signal to create new Player profile when a user is created
    """
    if created:
        PlayerProfile.objects.create(player=instance)
