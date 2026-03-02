from django.urls import path

from . import views

app_name = "Lobby"
urlpatterns = [
    path("", views.lobby_browser, name="lobby_browser"),
    path("new/", views.new_lobby_form, name="create_lobby"),
    path("insert/", views.insert_lobby, name="insert_lobby"),
    path("del/<int:lobby_id>", views.delete_lobby, name="delete_lobby"),

    path("<int:lobby_id>", views.view_lobby, name="view_lobby"),
    path("<int:lobby_id>/join/yamls", views.select_yamls, name="start_lobby_join"),
    path("<int:lobby_id>/join", views.join_lobby, name="join_lobby"),
]