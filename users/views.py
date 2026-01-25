from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from .models import users

# Create your views here.
def index(request):
    return HttpResponse('This is where the login page will go')

def account(request, user_id):
    try:
        user = get_object_or_404(users, pk=user_id)
        print(user.id)
        return render( request,
            'users/account.html',
            {"user": user,}
        )
    except KeyError:
        return HttpResponse('User not found')