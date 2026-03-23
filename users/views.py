from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.db import DatabaseError
from django.contrib import messages

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
    user = users.objects.filter(
        name = request.POST["name"]
    )

    if user:
        request.session['user_id'] = user[0].id
        return account(request, user[0].id)
    else:
        messages.error(request, "Invalid username")

    return render(request, 'users/login.html')

def logout(request):
    if request.session.get("user_id"):
        del request.session["user_id"]
    return HttpResponseRedirect(
        reverse(
            "home:home",
            args=()
        )
    )