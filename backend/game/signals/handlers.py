from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import logging

from game.models import PlayerProfile

logger = logging.getLogger(__name__)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_player_profile(sender, instance, created, **kwargs):
    """
    Uses the save signal to create new Player profile when a user is created
    """
    if created:
        logger.info('User created with ID: %s', instance.id)
        PlayerProfile.objects.create(player=instance)
