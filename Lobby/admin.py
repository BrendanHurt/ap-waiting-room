from django.contrib import admin

from .models import Lobby, LobbyConnection

# Register your models here.
admin.site.register(Lobby)
admin.site.register(LobbyConnection)