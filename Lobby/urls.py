from django.urls import path

from . import views

app_name = "Lobby"
urlpatterns = [
    path("", views.manage_lobbies, name="manage_lobbies"),
    path("new/", views.new_lobby_form, name="create_lobby"),
    path("insert/", views.insert_lobby, name="insert_lobby"),
    path("del/<int:lobby_id>", views.delete_lobby, name="delete_lobby"),
]