from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'login', LoginViewSet, basename='register')
router.register(r'player', PlayerViewset, basename='player')
router.register(r'create', RegisterViewSet, basename='createuser')
router.register(r'home', HomeView, basename='profile')


urlpatterns = [
    path('', include(router.urls)),
    path('verify/<int:pk>', LoginViewSet.as_view({'get': 'otp'})),
    path('forgetpassword', LoginViewSet.as_view({'get': 'forget_password'})),
    path('update/', LoginViewSet.as_view({'post': 'reset_password'})),

]