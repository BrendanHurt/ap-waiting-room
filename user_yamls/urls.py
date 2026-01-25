from django.urls import path

from . import views

app_name = "user_yamls"
urlpatterns = [
    path('<int:user_id>/', views.index, name='view_yamls'),
    path('add/', views.add, name='add_yaml'),
]