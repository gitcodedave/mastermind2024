from rest_framework.routers import DefaultRouter
from django.urls import path
from . import views

router = DefaultRouter()

router.register('playerprofiles', views.PlayerProfileViewSet)
router.register('games', views.GameViewSet)
router.register('rounds', views.RoundViewSet)
router.register('leaderboards', views.LeaderboardViewSet)

# URLConf
urlpatterns = router.urls + [
    path('newgame/', views.NewGameView.as_view(), name='new-game'),
    path('gamerounds/', views.RoundsView.as_view(), name='game-rounds'),
    path('leaderboard/', views.LeaderboardTotalsView.as_view(), name='leaderboard'),
    path('difficulty/', views.DifficultyConfigView.as_view(), name='get-difficulty')
]