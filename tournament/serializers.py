from datetime import datetime, timedelta
from users.models import user_reg
from rest_framework import serializers
from django.db import models
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_reg
        fields = ['id', 'groups']


class TournamentSerializer(serializers.ModelSerializer):
    total_player = models.IntegerField(null= False, blank= False)
    # match_type = serializers.SerializerMethodField()
    #
    # def get_match_type(self, object):
    #     return object.match_type

    def validate_tournament_name(self, object):
        t1 = Tournament.objects.filter(tournament_name=object)
        if t1:
            raise serializers.ValidationError("tournament name must be unique")
        return object

    def validate_Max_score(self, data):
        if data < 11:
            raise serializers.ValidationError("Max score must be more then 11")
        return data

    def validate_start_date(self, data):
        if data < datetime.today().date():
            raise serializers.ValidationError("start date must be after today")
        return data

    def validate_registration_end(self, data):
        startdate = self.initial_data.get('start_date')
        if startdate is None and self.instance:
            startdate = self.instance.start_date

        if startdate:
            if type(startdate) == str:
                startdate = datetime.strptime(startdate, '%Y-%m-%d').date()
            if startdate < data:
                raise serializers.ValidationError({"registration_start": "start date must be after registration date"})
            if data <= datetime.today().date():
                raise serializers.ValidationError("registration ends after today")
            return data
        raise serializers.ValidationError("missing required data")


    class Meta:
        model = Tournament
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        total = int(instance.total_players)
        for i in range(1, total):
            if pow(2, i) == total:
                enddate = instance.start_date + timedelta(days=i - 1)
                response['end_date'] = enddate
                instance.end_date = enddate
                instance.save()
        enddate = response['end_date']
        if instance.start_date > datetime.today().date():
            response['status'] = 'upcoming'
        elif enddate < datetime.today().date():
            response['status'] = "previous"
        else:
            response['status'] = "ongoing"
        response['match_type'] = response['match_type']
        return response

class MatchSerializer(serializers.ModelSerializer):
    player1_username = serializers.SerializerMethodField(read_only=True, required=False)
    player1_image = serializers.SerializerMethodField(read_only=True, required=False)

    player2_image = serializers.SerializerMethodField(read_only=True, required=False)
    player2_username = serializers.SerializerMethodField(read_only=True, required=False)

    winner_image = serializers.SerializerMethodField(read_only=True, required=False)
    winner_username = serializers.SerializerMethodField(read_only=True, required=False)

    status = serializers.SerializerMethodField(read_only=True, required=False)

    def get_player1_username(self, object):
        return object.player1.username

    def get_player1_image(self, object):
        return '/media/' + str(object.player1.image) if str(object.player1.image) else None

    def get_player2_username(self, object):
        return object.player2.username

    def get_player2_image(self, object):
        return '/media/' + str(object.player2.image) if str(object.player2.image) else None

    def get_winner_username(self, object):
        return object.winner.username if object.winner_id else None

    def get_winner_image(self, object):
        return '/media/' + str(object.winner.image) if object.winner_id and str(object.winner.image) else None

    def validate_game_date(self, data):
        if data < datetime.today().date():
            raise serializers.ValidationError("match date must be after today")
        return data

    def get_status(self,object):
        if object.game_date > datetime.today().date():
            status = "upcoming"
        elif object.game_date == datetime.today().date():
            status = "ongoing"
        else:
            status = "previous"
        return status

    def validate(self, data):
        player = int(
            Tournament.objects.filter(tournament_name=data['tournament']).values('total_players')[0]['total_players'])
        a = pow(2, data['round_number'])
        player = pow(2, player)
        if a > player:
            raise serializers.ValidationError("invalid round number")
        return data

    class Meta:
        model = MatchData
        fields = '__all__'


class SetSerializer(serializers.ModelSerializer):
    class Meta:
        model = SetData
        fields = '__all__'
