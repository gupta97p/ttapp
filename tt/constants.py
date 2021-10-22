from django.core.mail import send_mail


class error():
    roundnumber = "invalid round number"
    round_not_created = "round not created yet"


class message():
    pass


class mail():
    def email(self, request):
        print(request)
        # send_mail(request['subject'], request['message'], request['from'], [request['to']], )
