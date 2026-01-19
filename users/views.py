from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from .models import users

# Create your views here.
def index(request):
    return HttpResponse('This is where the login page will go')

def account(request, user_id):
    user = get_object_or_404(users, pk=user_id)
    return render(
        request,
        'users/account.html',
        {"user": user}
    )