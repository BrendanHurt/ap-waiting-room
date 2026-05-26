from django.urls import path

from . import views

app_name = "Lobby"
urlpatterns = [
    path("", views.lobby_browser, name="lobby_browser"),
    path("form", views.lobby_form, name="lobby_form"),
    path("form/<int:lobby_id>", views.lobby_form, name="lobby_form"),
    path("form/submit/", views.submit_lobby, name="submit_lobby"),
    path("form/submit/<slug:lobby_id>", views.submit_lobby, name="submit_lobby"),
    path("del/<int:lobby_id>", views.delete_lobby, name="delete_lobby"),

    path("<int:lobby_id>", views.view_lobby, name="view_lobby"),
    path("<int:lobby_id>/join/yamls", views.add_slot_form_view, name="add_slot_form"),
    path("<int:lobby_id>/join", views.add_slot_view, name="add_slot"),
    path("slot/del/<int:slot_id>", views.delete_slot_view, name="delete_slot"),
    path("slot/edit/<int:slot_id>", views.edit_slot_view, name="edit_slot"),
]