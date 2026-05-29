from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.db import DatabaseError
from django.urls import reverse

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Yaml

@login_required
def view_yamls(request, user_id):
    return render(request,
        'user_yamls/view_yamls.html',
    )

@login_required
def yaml_form(request, yaml_id=None):
    slot_name = Yaml._meta.get_field("slot_name").get_default()
    game_name = Yaml._meta.get_field("game_name").get_default()
    description = ""
    game_options = ""

    if (yaml_id is not None):
        yaml = get_object_or_404(Yaml, pk=yaml_id)
        slot_name = yaml.slot_name
        game_name = yaml.game_name
        description = yaml.description
        game_options = yaml.game_options
    
    return render( 
        request,
        'user_yamls/yaml_form.html',
        {
            "yaml_id": yaml_id,
            "slot_name": slot_name,
            "yaml_game_name": game_name,
            "yaml_description": description,
            "yaml_game_options": game_options
        },
    )

def submit_yaml(request, yaml_id=None):
    yaml = None
    if (yaml_id is not None):
        yaml = get_object_or_404(Yaml, pk=yaml_id)
    else:
        yaml = Yaml()
    yaml.user_id = request.user
    
    yaml.slot_name = request.POST["slot_name"]
    yaml.game_name = request.POST["game_name"]
    yaml.description = request.POST["description"]
    yaml.game_options = request.POST["game_options"]

    yaml.save()
    return HttpResponseRedirect(
        reverse(
            "user_yamls:view_yamls",
            args=(request.user.id,)
        )
    )

@login_required
def delete_yaml(request, yaml_id):
    yaml = Yaml.objects.get(pk = yaml_id)
    yaml.delete()
    return HttpResponseRedirect(
        reverse(
            "user_yamls:view_yamls",
            args=(request.user.id,)
        )
    )
    