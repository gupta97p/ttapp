from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'tournament', TournamentViewSet, basename='tournament')
router.register(r'match', MatchDataViewSet, basename='match')


urlpatterns = [
    path('', include(router.urls)),
    path('draw/', TournamentViewSet.as_view({'post': 'draws'})),
    path('draws/', TournamentViewSet.as_view({'post': 'drawsforrounds'})),
    path('score/', PlayerViewSet.as_view({'get': 'scorer'})),
    path('matchlist/', PlayerViewSet.as_view({'get': 'matchlist'})),
    path('getmatch/<int:pk>', PlayerViewSet.as_view({'get': 'get_match'})),
    path('gettournament/<int:pk>', PlayerViewSet.as_view({'get': 'get_tournament'})),
    path('tournamentlist/', PlayerViewSet.as_view({'post': 'tournament_list'})),
    path('upcoming/', PlayerViewSet.as_view({'get': 'upcoming'})),
    path('ongoing/', PlayerViewSet.as_view({'get': 'ongoing'})),
    path('previous/', PlayerViewSet.as_view({'get': 'previous'})),
    path('setdata/', MatchDataViewSet.as_view({'post': 'setcreate'}))

]
