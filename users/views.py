from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from .models import users

# Create your views here.
def index(request):
    return HttpResponse('This is where the login page will go')

def account(request, user_id):
    try:
        user = users.objects.get(pk=request.session["user_id"])
        return render(request,
            'users/account.html',
            {"user": user,}
        )
    except KeyError:
        return HttpResponse('Error accessing account page')

def user_auth(request):
    try:
        user = users.objects.get(
            name = request.POST["name"]
        )

        request.session['user_id'] = user.id
        
        return account(request, user.id)

    except (KeyError):
        return HttpResponse('Error while signing in')
#        return HttpResponseRedirect(
#            render(
#                request,
#                'home/login.html',
#               { 'error_message': 'Invalid login'},
#            )
#        )

def logout(request):
    if request.session.get("user_id"):
        del request.session["user_id"]
    return HttpResponseRedirect(
        reverse(
            "home:home",
            args=()
        )
    )