from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.timezone import now
from django.db import DatabaseError

from .models import Lobby, LobbyConnection
from users.models import users
from user_yamls.models import user_yamls

#----------------------------------------------
# Lobby Views

# Create your views here.
def manage_lobbies(request):
    user_id = request.session.get("user_id")
    filters = {
        "Hosting": True,
        "Joined": True,
    }
    lobbies = Lobby.objects.filter(host_id=user_id)
    return render(request, "Lobby/manage_lobbies.html", {"lobbies": lobbies})

def new_lobby_form(request):
    return render(request, "Lobby/create_lobby.html")

def insert_lobby(request):
    user = get_object_or_404(users, pk=request.session.get("user_id"))

    async_val = False
    if request.POST.get("is_async"):
        async_val = True

    lobby_name = request.POST.get("name")
    if not lobby_name:
        lobby_name = Lobby._meta.get_field("name").get_default()
    
    new_lobby = Lobby(
        host_id=user,
        name=lobby_name,
        start_date=request.POST["start_date"],
        is_async = async_val,
        description=request.POST["description"],
    )
    new_lobby.save()
    return HttpResponseRedirect(
        reverse(
            "Lobby:manage_lobbies",
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