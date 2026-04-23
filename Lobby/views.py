from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.timezone import now
from django.db import DatabaseError
from django.contrib import messages
from django.db.models.signals import post_save
from django.dispatch import receiver
from guardian.shortcuts import assign_perm

from .models import Lobby, LobbyConnection
from django.contrib.auth.models import User
from user_yamls.models import user_yamls

#----------------------------------------------
# Lobby Views

# Create your views here.
def lobby_browser(request):
    user_id = request.session.get("user_id")
    user = None
    if (User.objects.filter(id=user_id)):
        user = User.objects.filter(id=user_id).first()

    #add lobby filtering later
    lobbies = Lobby.objects.all()

    return render(
        request,
        "Lobby/lobby_browser.html",
        {
            "user": user,
            "lobbies": lobbies,
        },
    )

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

    return render(
        request,
        "Lobby/lobby_form.html",
        context,
    )

# TODO: Add logging to form submissions, successful or not
def submit_lobby(request, lobby_id=None):
    user = get_object_or_404(User, pk=request.session.get("user_id"))

    lobby = None
    if (lobby_id is not None):
        lobby = get_object_or_404(Lobby, pk=lobby_id)
    else:
        lobby = Lobby()
        lobby.host_id = user

    lobby.name = request.POST.get("name")
    lobby.start_date = request.POST.get("start_date")
    lobby.description = request.POST.get("description")
    async_val = False
    lobby.is_async = True if request.POST.get("is_async") else False

    lobby.save()
    return HttpResponseRedirect(
        reverse(
            "Lobby:lobby_browser",
            args=()
        )
    )

@receiver(post_save, sender=Lobby)
def assign_host_perms(sender, instance, created, **kwargs):
    if created:
        assign_perm("change_lobby", instance.host_id, instance)
        assign_perm("delete_lobby", instance.host_id, instance)
        assign_perm("view_lobby", instance.host_id, instance)


def delete_lobby(request, lobby_id):
    lobby = Lobby.objects.get(pk=lobby_id)
    lobby.delete()
    return HttpResponseRedirect(
        reverse(
            "Lobby:lobby_browser",
            args=()
        )
    )


def view_lobby(request, lobby_id):
    #get the lobby
    #then, get any yamls the current user has sent to this lobby
        #find yaml by user
    #add those to the context & send to the lobby info template
    lobby = get_object_or_404(Lobby, pk=lobby_id)
    conns = LobbyConnection.objects.filter(
        lobby_id_id=lobby_id
    )
    user = None
    if (request.session.has_key("user_id")):
        user = get_object_or_404(User, pk=request.session.get("user_id"));
    #ZZZ Figuring out how to display permitted actions for connection
    
    return HttpResponse(
        render(
            request, 
            "Lobby/lobby_connections_info.html",
            {"lobby": lobby, "conns": conns, "user": user,}
        )
    )

#----------------------------------------------
# Lobby Connection Views
def select_yamls(request, lobby_id):
    yaml_list = user_yamls.objects.filter(
        user_id=request.session.get("user_id")
    )
    request.session["lobby_id"] = lobby_id
    return HttpResponse(
        render(
            request,
            "Lobby/join_lobby_form.html",
            {"yaml_list": yaml_list, "lobby_id": lobby_id}
        ),
    )

def join_lobby(request, lobby_id):
    lobby = get_object_or_404(Lobby, pk=lobby_id)
    yaml_ids = request.POST.get("yaml_ids")
    if yaml_ids is None:
        messages.error(request, "You must select at least one YAML to join a lobby")
        return HttpResponseRedirect(
            reverse("Lobby:start_lobby_join", args=(lobby.id,))
        )
    
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

def delete_connection(request, slot_id):
    lobby_conn = get_object_or_404(LobbyConnection, pk=slot_id)
    lobby = lobby_conn.lobby_id
    lobby_conn.delete()
    return HttpResponseRedirect(
        reverse(
            "Lobby:view_lobby",
            kwargs={"lobby_id": lobby.id}
        )
    )

def edit_connection(request, slot_id):
    return HttpResponse("Temp Stub")

@receiver(post_save, sender=LobbyConnection)
def grant_view_lobby_permissions(sender, instance, created, **kwargs):
    #ZZZ
    #Add view lobby perm, if it doesn't already exist & a lobby connection is made
    #Add edit and delete permissions to the lobby connection:
    # -User can change the yaml used for the connection
    # -User has access to deleting the connection
    # -Removing the last connection doesn't revoke lobby view permissions,
    #  only the host can "kick" a player
    assign_perm("view_lobby", instance.player_yaml.user_id, instance.lobby_id)
    assign_perm("change_lobbyconnection", instance.player_yaml.user_id, instance)
    assign_perm("delete_lobbyconnection", instance.player_yaml.user_id, instance)