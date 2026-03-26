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

def yaml_form(request, yaml_id=None):
    yaml_slot = "Slot Name"

    slot = user_yamls._meta.get_field("slot").get_default()
    game_name = user_yamls._meta.get_field("game_name").get_default()
    description = ""
    game_options = ""

    if (yaml_id is not None):
        yaml = get_object_or_404(user_yamls, pk=yaml_id)
        slot = yaml.slot
        game_name = yaml.game_name
        description = yaml.description
        game_options = yaml.game_options
    print (slot)
    return render( 
        request,
        'user_yamls/yaml_form.html',
        {
            "yaml_id": yaml_id,
            "yaml_slot": slot,
            "yaml_game_name": game_name,
            "yaml_description": description,
            "yaml_game_options": game_options
        },
    )

def submit_yaml(request, yaml_id=None):
    #get the user_id
    #get the slot name
    #get the game name
    #get the description, emtpy string if none
    #get the options
    user = get_object_or_404(
        users,
        pk=request.session.get("user_id")
    )

    yaml = None
    if (yaml_id is not None):
        yaml = get_object_or_404(user_yamls, pk=yaml_id)
    else:
        yaml = user_yamls()
        yaml.user_id = user
    
    yaml.slot = request.POST["slot"]
    yaml.game_name = request.POST["game_name"]
    yaml.description = request.POST["description"]
    yaml.game_options = request.POST["game_options"]

    yaml.save()
    return HttpResponseRedirect(
        reverse(
            "user_yamls:view_yamls",
            args=(user.id,)
        )
    )

def delete_yaml(request, yaml_id):
    yaml = user_yamls.objects.get(pk = yaml_id)
    yaml.delete()
    return HttpResponseRedirect(
        reverse(
            "user_yamls:view_yamls",
            args=(request.session.get("user_id"),)
        )
    )
    