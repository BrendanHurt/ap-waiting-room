from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.timezone import now

from .models import Lobby, LobbyConnection
from users.models import users

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