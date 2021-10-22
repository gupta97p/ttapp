import random
import json
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from datetime import timedelta
from rest_framework.viewsets import ViewSet
from rest_framework.authtoken.models import Token
from .models import *
from .serializers import *
from users.models import user_reg
from rest_framework.decorators import permission_classes


@permission_classes((AllowAny,))
class PlayerViewSet(ViewSet):

    def upcoming(self, request):
        try:
            if request.GET:
                user = user_reg.objects.filter(id=request.GET.get('id')).first()
                if user.groups.filter(name='tournament_admin').exists():
                    queryset = Tournament.objects.filter(user_id=request.GET.get('id')).order_by('start_date')
                    serializer = TournamentSerializer(queryset, many=True)
                    result = []
                    for i in serializer.data:
                        if i['status'] == "upcoming":
                            result.append(i)
                    return Response(result)
            queryset = Tournament.objects.all().order_by('start_date')
            serializer = TournamentSerializer(queryset, many=True)
            result = []
            for i in serializer.data:
                if i['status'] == "upcoming":
                    result.append(i)
            return Response(result)
        except Exception as e:
            return Response("error " + str(e), 422)

    def previous(self, request):
        try:
            if request.GET:
                user = user_reg.objects.filter(id=request.GET.get('id')).first()
                if user.groups.filter(name='tournament_admin').exists():
                    queryset = Tournament.objects.filter(user_id=request.GET.get('id')).order_by('start_date')
                    serializer = TournamentSerializer(queryset, many=True)
                    result = []
                    for i in serializer.data:
                        if i['status'] == "previous":
                            result.append(i)
                    return Response(result)
            queryset = Tournament.objects.all().order_by('start_date')
            serializer = TournamentSerializer(queryset, many=True)
            result = []
            for i in serializer.data:
                if i['status'] == "previous":
                    result.append(i)
            return Response(result)
        except Exception as e:
            return Response("error encountered " + str(e), 422)

    def ongoing(self, request):
        try:
            if request.GET:
                user = user_reg.objects.filter(id=request.GET.get('id')).first()
                if user.groups.filter(name='tournament_admin').exists():
                    queryset = Tournament.objects.filter(user_id=request.GET.get('id')).order_by('start_date')
                    serializer = TournamentSerializer(queryset, many=True)
                    result = []
                    for i in serializer.data:
                        if i['status'] == "ongoing":
                            result.append(i)
                    return Response(result)
            queryset = Tournament.objects.all().order_by('start_date')
            serializer = TournamentSerializer(queryset, many=True)
            result = []
            for i in serializer.data:
                if i['status'] == "ongoing":
                    result.append(i)
            return Response(result)
        except Exception as e:
            return Response("error encountered: " + str(e), 422)

    def get_match(self, request, pk=None):
        try:
            queryset = MatchData.objects.filter(pk=pk).first()
            serializer = MatchSerializer(queryset)
            query = SetData.objects.filter(match_id=pk)
            tournament = Tournament.objects.filter(pk=queryset.tournament_id).first()
            result = []
            for j in query.values():
                dict = {}
                dict['set_id'] = j['id']
                dict['player1_score'] = j['score1']
                dict['player2_score'] = j['score2']
                dict['winner'] = j['set_winner_id']
                result.append(dict)
            return Response({'match_detail': serializer.data, "set_detail": result, "max_score": tournament.Max_score})
        except Exception as e:
            return Response({'message': str(e)}, 500)

    def get_tournament(self, request, pk=None):
        try:
            queryset = Tournament.objects.filter(pk=pk).first()
            draws = MatchData.objects.filter(tournament_id=pk)
            serializer_class = TournamentSerializer(queryset)
            username = []
            for i in queryset.player.values('username'):
                username.append(i['username'])
            if not draws:
                return Response({'torunament_detail': serializer_class.data, "match_list_available": "False"}, 200)
            return Response({'torunament_detail': serializer_class.data, "match_list_available": "True",
                             "tournament_winner": str(queryset.winner), "players": username}, 200)
        except Exception as e:
            return Response('error ' + str(e), 500)

    def tournament_list(self, request):
        queryset = Tournament.objects.filter(user_id=request.GET.get('id')).order_by('start_date')
        serializer = TournamentSerializer(queryset, many=True)
        li = []
        for i in serializer.data:
            result = {'id': i['id'], 'tournament_name': i['tournament_name'], 'start_date': i['start_date'],
                      'end_date': i['end_date'], 'registration_end': i['registration_end']}
            li.append(result)
        return Response(li)

    def scorer(self, request):
        try:
            result = []
            queryset = MatchData.objects.filter(id=request.GET.get('id')).first()
            query = SetData.objects.filter(match_id=request.GET.get('id'))
            for j in query.values():
                dict = {'player1_id': queryset.player1.username, 'player2_id': queryset.player2.username,
                        'set_id': j['id'], 'player1_score': j['score1'], 'player2_score': j['score2'],
                        'winner': j['set_winner_id']}
                result.append(dict)
            return Response(result)
        except Exception as e:
            return Response("error " + str(e), 500)

    # matchlist as per round
    def matchlist(self, request):
        try:
            t_obj = int(Tournament.objects.filter(id=request.GET.get('id')).first().total_players)
            for i in range(1, t_obj):
                if pow(2, i) == t_obj:
                    t_obj = i
                    break
            if 'round' in request.GET:
                queryset = MatchData.objects.filter(tournament_id=request.GET.get('id'), type__contains=request.GET.get('type'), round_number=request.GET.get('round'))
                if not queryset:
                    queryset = MatchData.objects.filter(tournament_id=request.GET.get('id'))
                    if not queryset:
                        return Response("invalid tournament id", 422)
                    return Response("round not created yet", 200)
                serializer = MatchSerializer(queryset, many=True)
                return Response({'data': serializer.data, "total_rounds": t_obj}, 200)
            else:
                queryset = MatchData.objects.filter(tournament_id=request.GET.get('id'), type__contains=request.GET.get('type'))
            serializer = MatchSerializer(queryset, many=True)
            round_list = {}
            for i in range(1, (t_obj + 1)):
                result = []
                for j in serializer.data:
                    if j['round_number'] == i:
                        result.append(j)
                if result:
                    round_list[f"round {i}"] = result
            return Response({'data': round_list, "total_rounds": t_obj}, 200)
        except Exception as e:
            return Response({'message ': str(e)}, 500)


class TournamentViewSet(ViewSet):
    def create(self, request):
        try:
            token = Token.objects.get(key=(request.META.get('HTTP_AUTHORIZATION'))[6:]).user
            serializer = TournamentSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({'status': 'failed', 'data': {'message': serializer.errors}}, 422)
            ser_instance = serializer.save()
            ser_instance.user_id = token.id
            ser_instance.save()
            return Response({'message': 'record Saved successfully'}, 200)
        except Exception as e:
            return Response({'message': str(e)}, 500)

    def update(self, request, pk=None):
        try:
            tournament_detail = Tournament.objects.get(pk=pk)
            if tournament_detail.end_date < datetime.today().date():
                return Response({"status": "failed", "message": "Tournament is completed"}, 422)
            serializer = TournamentSerializer(tournament_detail, data=request.data, partial=True)
            if not serializer.is_valid():
                return Response({'status': 'failed', 'data': {"message": serializer.errors}}, 422)
            serializer.save()
        except Exception as e:
            return Response('error : ' + str(e), 500)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        try:
            user_detail = Tournament.objects.get(pk=pk)
            user_detail.delete()
        except Exception as e:
            return Response('some exception occurred ' + str(e), 500)
        return Response('record Deleted successfully')

    def draws(self, request):
        try:
            queryset = Tournament.objects.get(id=request.data['tournament_id'])
            max_player = queryset.total_players
            player_list = json.loads(request.data['players'])
            if str(len(player_list)) != max_player:
                return Response({'error message': f"select {max_player} players"}, 422)
            player_li = player_list.copy()
            final_list = []
            for i in range(int((len(player_list) / 2))):
                drawlist = {'tournament': request.data['tournament_id'], 'round_number': 1,
                            'game_date': queryset.start_date, 'type': request.data['type'], 'score': queryset.Max_score}
                random_number = random.choice(player_li)
                drawlist['player1'] = random_number
                queryset.player.add(random_number)
                player_li.remove(random_number)
                random_number = random.choice(player_li)
                drawlist['player2'] = random_number
                queryset.player.add(random_number)
                player_li.remove(random_number)
                final_list.append(drawlist)
                serializer = MatchSerializer(data=drawlist)
                if not serializer.is_valid():
                    return Response({'message': serializer.errors}, 422)
                serializer.save()
            return Response(final_list)
        except Exception as e:
            return Response("error " + str(e), 500)


class MatchDataViewSet(ViewSet):
    # set create and match winner
    def partial_update(self, request, pk=None):
        try:
            user_detail = MatchData.objects.get(pk=pk)
            serializer = MatchSerializer(user_detail, data=request.data, partial=True)
            if not serializer.is_valid():
                return Response({'data': serializer.errors}, 422)
            serializer.save()
        except Exception as e:
            return Response('some exception occured' + str(e), 500)
        return Response(serializer.data)

    def drawsforrounds(self, request):
        try:
            match = MatchData.objects.filter(tournament=request['id'], round_number=request['roundn'], type=request['type'])
            total = match.values().count()
            winners = 0
            for i in match.values():
                if i['winner_id']:
                    winners = winners + 1
            if winners < total:
                return "wait"
            instance = Tournament.objects.filter(id=request['id']).first()
            round = int(request['roundn'])
            player_li, final_list, draw_list = [], [], {}
            matchinstance = match.filter(round_number=round, type=request['type'])
            for i in matchinstance:
                player_li.append(i.winner_id)
            player_list = player_li.copy()
            gamedate = instance.start_date + timedelta(days=round)
            for i in range(int((len(player_list) / 2))):
                drawlist = {'tournament': request['id'], 'round_number': round + 1, 'game_date': gamedate, "type": request['type'],
                            'score': queryset.Max_score}
                random_number = random.choice(player_li)
                drawlist['player1'] = random_number
                player_li.remove(random_number)
                random_number = random.choice(player_li)
                drawlist['player2'] = random_number
                player_li.remove(random_number)
                final_list.append(drawlist)
                serializer = MatchSerializer(data=drawlist)
                if not serializer.is_valid():
                    return {'message': serializer.errors}, 422
                serializer.save()
            return 'done'
        except Exception as e:
            return "error " + str(e), 500

    # match update
    def create(self, request):
        try:
            matchid = request.data['match']
            if 'give_bye' in request.data:
                match_obj = MatchData.objects.filter(id=matchid).first()
                match_obj.winner_id = request.data['give_bye']
                match_obj.save()
                return Response({"match_winner": match_obj.winner_id})
            serializer = SetSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({'message': serializer.errors}, 422)
            serializer.save()
            obj = SetData.objects.filter(match=matchid)
            total = obj.values().count()
            if total <= 3:
                result = []
                for i in obj.values():
                    if i['set_winner_id'] not in result:
                        result.append(i['set_winner_id'])
                    else:
                        matchobj = MatchData.objects.filter(pk=matchid).first()
                        matchobj.winner_id = i['set_winner_id']
                        matchobj.save()
                        t_id = matchobj.tournament_id
                        user1obj = user_reg.objects.filter(pk=matchobj.player1_id).first()
                        user2obj = user_reg.objects.filter(pk=matchobj.player2_id).first()
                        if i['set_winner_id'] == user1obj.id:
                            user1obj.match_played = user1obj.match_played + 1
                            user1obj.match_won = user1obj.match_won + 1
                            i['set_winner_id'] = user1obj.username
                            user1obj.save()
                        else:
                            user1obj.match_played = user1obj.match_played + 1
                            user1obj.save()
                        if i['set_winner_id'] == user2obj.id:
                            user2obj.match_played = user2obj.match_played + 1
                            user2obj.match_won = user2obj.match_won + 1
                            i['set_winner_id'] = user2obj.username
                            user2obj.save()
                        else:
                            user2obj.match_played = user2obj.match_played + 1
                            user2obj.save()
                        match_obj = MatchData.objects.filter(tournament_id=t_id, type=matchobj.type)
                        t_obj = Tournament.objects.filter(id=t_id).first()
                        pla = int(t_obj.total_players)
                        winners = 0
                        for j in match_obj.values():
                            if j['winner_id']:
                                winners += 1
                        if winners == (pla - 1):
                            winner = match_obj.last().winner_id
                            user = user_reg.objects.filter(id=winner).first()
                            if t_obj.winner:
                                t_obj.winner.append(user.id)
                            else:
                                t_obj.winner = user.id
                            t_obj.save()
                        roundn = match_obj.last().round_number
                        type = match_obj.last().type
                        draws = {"id": t_id, "roundn": roundn, "type": type}
                        self.drawsforrounds(draws)
                        return Response({"winner_match": i['set_winner_id']})
            val = total - 1
            return Response({'winner_set': obj.values('set_winner_id')[val]})
        except Exception as e:
            return Response('some exception occurred' + str(e))

    # def setcreate(self, request):
    #     try:
            # match_obj = MatchData.objects.filter(pk=request.data['match'])
            # tournament_obj = Tournament.objects.filter(tournament_name=match_obj.first().tournament)
            # max_score = tournament_obj.first().Max_score
            # if request.data['score1'] >= max_score-1 or request.data['score1'] >= max_score-1:
            #     if request.data['score1'] == request.data['score2']:
            #         tournament_obj.first().Max_score = max_score + 1
            #     else:
            #         pass
            # set_data = SetData.objects.filter(match=request.data['match'])
            # if not set_data:
            #     serializer = SetSerializer(data=request.data)
            # else:
            #     total_set = set_data.values().count()
            #     if total_set <= 2:
            #         if set_data.last().set_winner:
            #             serializer = SetSerializer(data=request.data)
            #         else:
            #             serializer = SetSerializer(set_data.last(), data=request.data, partial=True)
            #     else:
            #         serializer = SetSerializer(set_data.last(), data=request.data, partial=True)
            # if not serializer.is_valid():
            #     return Response("some error occurred " + serializer.errors)
            # serializer.save()
            # return Response("successful")
        # except Exception as e:
        #     return Response("some error occurred " + str(e))
