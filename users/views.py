from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.db import DatabaseError
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

@login_required(login_url="/login/")
def account(request, user_id):
    try:
        user = User.objects.get(pk=request.session["user_id"])
        return render(request,
            'users/account.html',
            {"user": user,}
        )
    except KeyError:
        return HttpResponse('Error accessing account page')

def login_view(request):
    return render(request, "users/login.html")

def validate_auth(request):
    if (request.method != "POST"):
        return render(request, "users/login.html")
    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username=username, password=password)

    if user is not None:
        request.session['user_id'] = user.id
        login(request, user)
        print(user.id)
        return account(request, user.id)
    else:
        messages.error(request, "Invalid login")
        return render(request, 'users/login.html')

#ZZZ Need to figure out how to remove session ID, to *actually* sign out
@login_required()
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(
        reverse(
            "home:home",
            args=()
        )
    )

def register_form(request):
    return render(request, "users/register_form.html")

def register_user(request):

    #password = request.POST.get("password")
    #ap_token = request.POST.get("ap_token")

    
    username = request.POST.get("username")
    email = request.POST.get("email")
    password = request.POST.get("password")
    newUser = User.objects.create_user(
        username, email, password
    )
    newUser.save()

    authenticate(username)

    request.session["user_id"] = newUser.id
    return HttpResponseRedirect(
        reverse(
            "home:home",
            args=()
        )
    )
