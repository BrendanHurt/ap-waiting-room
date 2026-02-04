from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.db import DatabaseError
from django.urls import reverse

from users.models import users
from .models import user_yamls

# Create your views here.
def index(request, user_id):
    user = get_object_or_404(users, pk=user_id)
    return render(request,
        'user_yamls/view_yamls.html',
        { "user": user }
    )
    #return HttpResponse('This is the index page for yamls')

def yaml_form(request):
    return render(request, 'user_yamls/add_yaml.html')

def add(request):
    #get the user_id
    #get the slot name
    #get the game name
    #get the description, emtpy string if none
    #get the options
    try:
        user = get_object_or_404(
            users,
            pk=request.session.get("user_id")
        )
        new_yaml = user_yamls(
            user_id = user,
            slot = request.POST["slot"],
            game_name = request.POST["game_name"],
            description = request.POST["description"],
            game_options = request.POST["game_options"]
        )

        new_yaml.save()
        return HttpResponseRedirect(
            reverse(
                "user_yamls:view_yamls",
                args=(user.id,)
            )
        )
    except DatabaseError:
        return HttpResponse(DatabaseError)

def delete_yaml(request, yaml_id):
    yaml = user_yamls.objects.get(pk = yaml_id)
    yaml.delete()
    return HttpResponseRedirect(
        reverse(
            "user_yamls:view_yamls",
            args=(request.session.get("user_id"),)
        )
    )
    