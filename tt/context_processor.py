from tournament.models import Tournament, MatchData
from users.models import user_reg

def dashboard_count(request):
    if "/admin/" == request.META['PATH_INFO']:
        tournament_admin = user_reg.objects.filter(groups__name="tournament_admin").count()
        players = user_reg.objects.filter(groups__name="player").count()
        matches = MatchData.objects.all().count()
        tournament = Tournament.objects.all().count()
        return {"dashboard_count": {'players': players, 'match': matches, 'tournaments': tournament,
                                    'tournament_admin': tournament_admin}}
    return {"dashboard_count": {None}}
