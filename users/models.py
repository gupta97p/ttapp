from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager
from PIL import Image


class user_reg(AbstractUser):
    username = models.CharField(max_length=20, unique=True, blank=False)
    mobile = models.CharField(max_length=10, blank=True, null=True, unique=True)
    age = models.IntegerField(validators=[MinValueValidator(0)], null=True, blank=True)
    gender = models.CharField(max_length=8, default='Male')
    image = models.ImageField(upload_to='users/image', default='dummy/user.jpg')
    match_played = models.IntegerField(validators=[MinValueValidator(0)], null=True, blank=True, default=0,
                                       verbose_name='match played')
    match_won = models.IntegerField(validators=[MinValueValidator(0)], null=True, blank=True, default=0,
                                    verbose_name='match won')
    rank = models.IntegerField(validators=[MinValueValidator(0)], null=False, blank=True, default=0,
                               verbose_name='rank')

    objects = UserManager()

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        image = Image.open(self.image.path)
        image.save(self.image.path, quality=20, optimize=True)

class Verification_Otp(models.Model):
    user = models.ForeignKey(user_reg, on_delete=models.CASCADE, null=False)
    expired = models.CharField(max_length=10, null=True)
    pending = models.CharField(max_length=10, null=True)
    used = models.CharField(max_length=10, null=True, blank=True)
    created_at = models.DateTimeField()
