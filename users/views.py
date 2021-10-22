import uuid
from datetime import datetime, timedelta

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group

from rest_framework.authtoken.models import Token
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from tournament.models import Tournament
from tournament.serializers import TournamentSerializer

from .serializers import *


def authenticate_user(email, password):
    try:
        user = user_reg.objects.get(email=email)
    except user_reg.DoesNotExist:
        return None
    else:
        if user.check_password(password):
            return user
        return None


# user classes
@permission_classes((AllowAny,))
class LoginViewSet(ViewSet):
    def create(self, request):
        try:
            user = authenticate_user(request.data['username'], request.data['password'])
            if not user:
                user = authenticate(request, username=request.data['username'], password=request.data['password'])
            if not user:
                return Response({"status": "failed", 'message': 'invalid credentials'}, 401)
            if user.groups.filter(name="tournament_admin").exists():
                user_group = "tournament_admin"
            else:
                user_group = "player"
            otp_obj = Verification_Otp.objects.filter(user=user.id).first()
            if user.is_staff != True:
                otp = randint(100000, 1000000)
                otp_dict = {'user': user.id, 'pending': otp, 'created_at': datetime.now()}
                if not otp_obj:
                    otpdata = OtpSerializer(data=otp_dict)
                    if not otpdata.is_valid():
                        return Response({"status": "failed", "some error occurred ": otpdata.errors}, 422)
                    otpdata.save()
                else:
                    otp_obj.expired = otp_obj.pending
                    otp_obj.pending = otp
                    otp_obj.created_at = datetime.now()
                    otp_obj.save()
                send_mail("email verification", f"your verification code is {otp}", 'innocentgupta97@gmail.com',
                          [user.email], fail_silently=False)
                return Response(
                    {"status": "success", "message": "login successful please enter otp", "user_id": user.id})
            token, created = Token.objects.get_or_create(user_id=user.id)
            return Response({'message': f"Welcome {user}", 'user_id': user.id, 'user_group': user_group,
                             'data': dict(Tournament.PLAYER_CHOICES_LIST), "token": token.key}, 200)
        except Exception as e:
            return Response({"status": "failed", 'message': str(e)}, 500)

    def otp(self, request, pk=None):
        try:
            user = user_reg.objects.filter(pk=pk).first()
            otp_obj = Verification_Otp.objects.filter(user=pk).first()
            now = datetime.now().replace(tzinfo=None, microsecond=0).time()
            time = (otp_obj.created_at + timedelta(seconds=60)).replace(microsecond=0).time()
            if now < time:
                if request.GET.get('otp') == otp_obj.pending:
                    if user.is_staff:
                        otp_obj.used = otp_obj.pending
                        otp_obj.pending = None
                        user.save()
                        token, created = Token.objects.get_or_create(user_id=user.id)
                        return Response({"message": "password changed successfully", "token": token.key})
                    otp_obj.used = otp_obj.pending
                    otp_obj.pending = None
                    user.is_staff = True
                    user.save()
                    token, created = Token.objects.get_or_create(user_id=user.id)
                    if user.groups.filter(name="tournament_admin").exists():
                        user_group = "tournament_admin"
                    else:
                        user_group = "player"
                    return Response({"user_id": user.id, "token": token.key, "user_group": user_group}, 200)
                else:
                    return Response({"status": "failed", "message": "Please enter correct otp"}, 422)
            else:
                return Response({"status": "failed", "message": "otp timeout"}, 422)
        except Exception as e:
            return Response("some error occurred " + str(e), 422)

    def reset_password(self, request):
        try:
            otp_obj = Verification_Otp.objects.filter(pending=request.GET.get('otp')).first()
            if not otp_obj:
                return Response({"status": "failed", "message": "invalid otp"}, 500)
            user = user_reg.objects.get(pk=otp_obj.user_id)
            if user.groups.filter(name="player").exists():
                time = (otp_obj.created_at + timedelta(days=365)).replace(tzinfo=None, microsecond=0)
                user.is_staff = True
            else:
                time = (otp_obj.created_at + timedelta(minutes=5)).replace(tzinfo=None, microsecond=0)
            now = datetime.now().replace(tzinfo=None, microsecond=0)
            if now > time:
                otp_obj.expired = otp_obj.pending
                otp_obj.pending = None
                otp_obj.save()
                return Response({"status": "failed", "message": "otp timeout"})
            otp_obj.used = otp_obj.pending
            otp_obj.pending = None
            otp_obj.save()
            user.set_password(request.data['password'])
            user.save()
            return Response({"password changed successfully, please login to continue"}, 200)
        except Exception as e:
            return Response("some exception occurred  " + str(e), 500)

    def forget_password(self, request):
        try:
            user = user_reg.objects.filter(email=request.GET.get('email')).first()
            if user != None:
                otp = 'http://139.59.16.180:5002/reset_password/'
                token = uuid.uuid4().hex[:10]
                otp_obj = Verification_Otp.objects.filter(user=user.id).first()
                if otp_obj:

                    otp_obj.expired = otp_obj.pending
                    otp_obj.pending = token
                    otp_obj.created_at = datetime.now()
                    otp_obj.save()
                    otp = otp + token
                    send_mail("Password reset", f"Your password reset link is {otp}",
                              'welcome@gmail.com', [user.email], fail_silently=False)
                else:
                    otp_dict = {'user': user.id, 'pending': token, 'created_at': datetime.now()}
                    otpdata = OtpSerializer(data=otp_dict)
                    if not otpdata.is_valid():
                        return Response({"status": "failed", "some error occurred ": otpdata.errors}, 422)
                    otpdata.save()
                return Response({"message": "otp sent to the mail address", "data": user.id})
            else:
                return Response({"status": "failed", "message": "email id doesn't exit"}, 422)
        except Exception as e:
            return Response("some error occurred" + str(e), 422)


@permission_classes((AllowAny,))
class RegisterViewSet(ViewSet):
    # create user
    def create(self, request):
        try:
            serializer = RegisterSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({"status": "failed", 'message': serializer.errors}, 422)
            ser_instance = serializer.save()
            group = Group.objects.get(name='tournament_admin')
            ser_instance.groups.add(group.id)
            ser_instance.save()
            return Response({'message': 'record Saved successfully', 'data': serializer.data}, 200)
        except Exception as e:
            return Response({"status": "failed", 'message': str(e)}, 500)


class PlayerViewset(ViewSet):
    # create player
    def create(self, request):
        try:
            serializer = PlayerSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({'message': serializer.errors}, 422)
            ser_instance = serializer.save()
            group = Group.objects.get(name='player')
            ser_instance.groups.add(group.id)
            otp = uuid.uuid4().hex[:10]
            otp_dict = {'user': ser_instance.id, 'pending': otp, 'created_at': datetime.now()}
            otp = 'http://139.59.16.180:5002/reset_password/' + otp
            otpdata = OtpSerializer(data=otp_dict)
            if not otpdata.is_valid():
                return Response({"status": "failed", "some error occurred ": otpdata.errors}, 422)
            otpdata.save()
            print("otpobj valid")
            send_mail(f"welcome {ser_instance.username}",
                      f"You are added to auriga as a TT player. Please click on the "
                      f"link to generate your password {otp}", 'innocentgupta97@gmail.com',
                      [request.data['email']], fail_silently=False)
            print("mail sent")

            return Response({'message': 'record Saved successfully', 'data': serializer.data}, 200)
        except Exception as e:
            return Response({"status": "failed", 'message': str(e)}, 500)

class HomeView(ViewSet):

    def partial_update(self, request, pk=None):
        try:
            # token = Token.objects.get(key=(request.META.get('HTTP_AUTHORIZATION'))[6:]).user
            user_detail = user_reg.objects.filter(pk=pk).first()
            serializer = RegisterSerializer(user_detail, data=request.data, partial=True)
            if not serializer.is_valid():
                return Response({"status": "failed", 'data': serializer.errors}, 422)
            serializer.save()
            if 'password' in request.data:
                user_detail.password = make_password(request.data['password'], hasher='default')
                user_detail.save()
        except Exception as e:
            return Response('some exception occurred' + str(e), 500)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            queryset = user_reg.objects.get(pk=pk)
            serializer_class = RegisterSerializer(queryset)
            query = Tournament.objects.filter(player__id=queryset.id)
            t_ser = TournamentSerializer(query, many=True)
            return Response({"user_detail": serializer_class.data, 'played_tournaments': t_ser.data})
        except Exception as e:
            return Response("error " + str(e), 500)

    def list(self, request):
        if 'gender' in request.GET:
            gender = request.GET.get('gender')
            queryset = user_reg.objects.filter(groups__name='player', gender=gender).order_by('username')
        else:
            queryset = user_reg.objects.filter(groups__name='player').order_by('username')
        serializer_class = RegisterSerializer(queryset, many=True)
        result = []
        if 'username' in request.GET:
            for i in serializer_class.data:
                if request.GET.get('username') in i['username']:
                    result.append(i)
            return Response(result)
        return Response(serializer_class.data)

    def destroy(self, request, pk=None):
        try:
            user_detail = user_reg.objects.get(pk=pk)
            user_detail.delete()
        except Exception as e:
            return Response('some exception occurred ' + str(e), 500)
        return Response('record Deleted successfully')
