from django.contrib import admin
from django.contrib.admin import ModelAdmin, StackedInline
from datetime import timedelta, datetime
from django import forms
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import *

class TournamentValidation(forms.ModelForm):
    class meta:
        model = Tournament

    def clean(self):
        data = self.cleaned_data
        t_obj = Tournament.objects.filter(tournament_name=data['tournament_name'])
        if t_obj.count() > 1:
            raise forms.ValidationError("tournament name must be unique")
        start_date = data['start_date']
        registration_end = data['registration_end']
        players = int(data['total_players'])
        end_date = start_date + timedelta(days=players)
        if data['Max_score'] <= 10:
            raise forms.ValidationError("Max score must be greater then or equal to 11")
        self.instance.end_date = end_date
        if start_date <= registration_end:
            raise forms.ValidationError("start date must be after registration date")
        if registration_end <= datetime.now().date():
            raise forms.ValidationError("registration must end after today")
        return self.cleaned_data


class TournamentModelAdmin(ModelAdmin):
    def winner_link(self, Tournament):
        if Tournament.winner:
            url = reverse("admin:users_user_reg_change", args=[Tournament.winner.id])
            link = '<a href="%s">%s</a>' % (url, Tournament.winner)
            return mark_safe(link)

    readonly_fields = ('user_id', 'winner')
    form = TournamentValidation
    empty_value_display = 'winner yet to be declared'
    fields = ('tournament_name', 'start_date', 'registration_end', 'Max_score', 'image', 'total_players', 'winner',
              'user_id')
    list_display = ('tournament_name', 'winner', 'start_date', 'registration_end', 'user', 'Max_score', 'total_players')
    list_display_links = ('tournament_name', 'winner')

    # ModelAdmin.actions_on_bottom = True
    # search_fields = ('tournament_name',)
    # actions_selection_counter = True

    # reverse(Tournament.winner)
    # author_link.short_description = 'Author'
    # search_fields = (None,) # ['tournament_name']
    # def get_actions(self, request):
    #     actions = super().get_actions(request)
    #     if request.user.is_superuser:
    #
    #         if 'delete_selected' in actions:
    #             del actions['delete_selected']
    #         else:
    #             return "you dont have permission"
    #     return actions
    class Meta:
        model = Tournament
        fields = '__all__'

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()


class MatchValidation(forms.ModelForm):
    class Meta:
        model = MatchData
        exclude = ()

    def clean(self):
        data = self.cleaned_data
        if data['game_date'] < datetime.today().date():
            raise forms.ValidationError("game date must be after today")
        return self.cleaned_data


class SetModelAdmin(StackedInline):
    model = SetData
    # fields = ['set_winner', 'score1', 'score2']



class MatchModelAdmin(ModelAdmin):
    # date_hierarchy = 'game_date'
    readonly_fields = ('tournament', 'player1', 'player2')
    empty_value_display = 'match not finished yet'
    fields = ('tournament', 'player1', 'player2', 'game_date', 'round_number', )
    list_display = ('tournament', 'player1', 'player2', 'round_number', 'winner')
    form = MatchValidation
    inlines = [SetModelAdmin]

    class Meta:
        model = MatchData
        fields = '__all__'


admin.site.register(Tournament, TournamentModelAdmin)
admin.site.register(MatchData, MatchModelAdmin)
