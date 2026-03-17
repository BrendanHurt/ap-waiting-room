from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.timezone import now
from django.db import DatabaseError
from django.contrib import messages
from django.db.models.functions import Extract

from .models import Lobby, LobbyConnection
from users.models import users
from user_yamls.models import user_yamls

#----------------------------------------------
# Lobby Views

# Create your views here.
def lobby_browser(request):
    user_id = request.session.get("user_id")
    filters = {
        "Hosting": True,
        "Joined": True,
    }
    lobbies = Lobby.objects.filter(host_id=user_id)
    return render(request, "Lobby/lobby_browser.html", {"lobbies": lobbies})

#Handles both creation & updating of lobbies
#Gets the default values for the model. Then, if there is a lobby_id passed in,
#overwrites those values with the lobby's data.
def lobby_form(request, lobby_id=None):
    lobby_name = Lobby._meta.get_field("name").get_default()
    lobby_start_date = Lobby._meta.get_field("start_date").get_default()
    lobby_description = Lobby._meta.get_field("description").get_default()
    lobby_async = Lobby._meta.get_field("is_async").get_default()

    if (lobby_id is not None):
        lobby = get_object_or_404(Lobby, pk=lobby_id)
        lobby_name = lobby.name
        lobby_start_date = lobby.start_date.isoformat()
        lobby_description = lobby.description
        lobby_async = lobby.is_async

    context = {
        "lobby_id": lobby_id,
        "lobby_name": lobby_name,
        "lobby_start_date": lobby_start_date,
        "lobby_description": lobby_description,
        "lobby_async": lobby_async,
    }

    print(context)

    return render(
        request,
        "Lobby/lobby_form.html",
        context,
    )

# TODO: Add logging to form submissions, successful or not
def submit_lobby(request, lobby_id=None):
    user = get_object_or_404(users, pk=request.session.get("user_id"))

    lobby = None
    if (lobby_id is not None):
        lobby = get_object_or_404(Lobby, pk=lobby_id)
    else:
        lobby = Lobby()
        lobby.host_id = user

    lobby_name = request.POST.get("name")
    lobby_start_date = request.POST.get("start_date")
    lobby_description = request.POST.get("description")
    async_val = False
    if request.POST.get("is_async"):
        async_val = True

    lobby.name = lobby_name
    lobby.start_date = lobby_start_date
    lobby.description = lobby_description
    lobby.is_async = async_val

    lobby.save()
    return HttpResponseRedirect(
        reverse(
            "Lobby:lobby_browser",
            args=()
        )
    )
    

def delete_lobby(request, lobby_id):
    lobby = Lobby.objects.get(pk=lobby_id)
    lobby.delete()
    return HttpResponseRedirect(
        reverse(
            "Lobby:manage_lobbies",
            args=()
        )
    )


def view_lobby(request, lobby_id):
    #get the lobby
    #then, get any yamls the current user has sent to this lobby
        #find yaml by user
    #add those to the context & send to the lobby info template
    lobby = get_object_or_404(Lobby, pk=lobby_id)
    yamls = user_yamls.objects.filter(
        lobbyconnection__lobby_id=lobby_id

    )
    
    return HttpResponse(
        render(
            request, 
            "Lobby/lobby_connections_info.html",
            {"lobby": lobby, "yamls": yamls}
        )
    )

#----------------------------------------------
# Lobby Connection Views
def select_yamls(request, lobby_id):
    yaml_list = user_yamls.objects.filter(pk=request.session.get("user_id"))
    request.session["lobby_id"] = lobby_id
    return HttpResponse(
        render(
            request,
            "Lobby/select_yaml.html",
            {"yaml_list": yaml_list, "lobby_id": lobby_id}
        ),
    )

def join_lobby(request, lobby_id):
    lobby = get_object_or_404(Lobby, pk=lobby_id)
    yaml_ids = request.POST["yaml_ids"]

    for yaml_id in yaml_ids:
        yaml = get_object_or_404(user_yamls, pk=yaml_id)
        try:
            l = LobbyConnection.objects.create(
                lobby_id=lobby,
                player_yaml=yaml
            )
        except DatabaseError:
            messages.error(request, "Failed to send yaml %s" %yaml_id)

    return HttpResponseRedirect(
        reverse(
            "Lobby:view_lobby",
            kwargs={"lobby_id": lobby_id}
        )
    )