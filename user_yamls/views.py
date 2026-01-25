from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from users.models import users

# Create your views here.
def index(request, user_id):
    user = get_object_or_404(users, pk=user_id)
    return render(request,
        'user_yamls/view_yamls.html',
        { "user": user }
    )
    #return HttpResponse('This is the index page for yamls')

def add(request):
    return HttpResponse('You have reached the add a yaml page. Please leave your message after the beep... beep')