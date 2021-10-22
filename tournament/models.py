from django.db import models
from users.models import user_reg
from django.core.validators import MinValueValidator
from PIL import Image
from django_mysql.models import ListCharField


class Tournament(models.Model):
    PLAYER_CHOICES_LIST = (
        ("2", "2"),
        ("4", "4"),
        ("8", "8"),
        ("16", "16"),
        ("32", "32"),
        ("64", "64"),
    )
    MATCH_CHOICE_LIST = (
        ("Men's single", "Men's single"),
        ("Men's double", "Men's double"),
        ("Women's single", "Women's single"),
        ("Women's double", "Women's double"),
        ("Mixed single", "Mixed single"),
        ("mixed double", "mixed double"),
    )

    tournament_name = models.CharField(max_length=50, blank=False, default='tt tournament')
    image = models.ImageField(upload_to="tournament/images", default='dummy/tournament.jpg')
    start_date = models.DateField(auto_now=False, blank=False)
    registration_end = models.DateField(auto_now=False, blank=False)
    Max_score = models.IntegerField(validators=[MinValueValidator(0)], null=False, blank=False)
    end_date = models.DateField(auto_now=False, blank=False, null=True)
    total_players = models.CharField(max_length=10, choices=PLAYER_CHOICES_LIST, default='2')
    status = models.CharField(max_length=8, blank=True, default='upcoming')
    match_type = ListCharField(base_field=models.CharField(max_length=14, choices=MATCH_CHOICE_LIST, null=True),
                               size=6, null=True, blank=False, max_length=(6 * 20))
    winner = ListCharField(base_field=models.IntegerField(null=True), max_length=(3 * 10), size=3, null=True)
    player = models.ManyToManyField(user_reg, blank=True, default=list)
    user = models.ForeignKey(user_reg, on_delete=models.CASCADE, related_name='user_reg4', null=True)

    def __str__(self):
        return self.tournament_name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        image = Image.open(self.image.path)
        image.save(self.image.path, quality=20, optimize=True)


class MatchData(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, default=1)
    score = models.IntegerField(null=True)
    player1 = models.ForeignKey(user_reg, on_delete=models.CASCADE, related_name='user_reg1')
    player2 = models.ForeignKey(user_reg, on_delete=models.CASCADE, related_name='user_reg2')
    winner = models.ForeignKey(user_reg, on_delete=models.CASCADE, blank=True, null=True)
    round_number = models.IntegerField(validators=[MinValueValidator(0)], verbose_name='round')
    game_date = models.DateField(auto_now=False)

    def __str__(self):
        return str(self.tournament)


class SetData(models.Model):
    match = models.ForeignKey(MatchData, on_delete=models.CASCADE)
    score1 = models.IntegerField(validators=[MinValueValidator(0)], blank=False, null=True, default=0)
    score2 = models.IntegerField(validators=[MinValueValidator(0)], blank=False, null=True, default=0)
    set_winner = models.ForeignKey(user_reg, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return str(self.match)
