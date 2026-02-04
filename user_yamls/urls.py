from django.urls import path

from . import views

app_name = "user_yamls"
urlpatterns = [
    path('<int:user_id>/', views.index, name='view_yamls'),
    path('yaml/', views.yaml_form, name='yaml_form'),
    path('yaml/save/', views.add, name='add_yaml'),
    path('yaml/del/<int:yaml_id>/', views.delete_yaml, name="del"),
]