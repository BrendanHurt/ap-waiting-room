from django.urls import path

from . import views

app_name = "user_yamls"
urlpatterns = [
    path('<int:user_id>/', views.index, name='view_yamls'),
    path('yaml/', views.yaml_form, name='yaml_form'),
    path('yaml/<slug:yaml_id>', views.yaml_form, name='yaml_form'),
    path('yaml/submit/', views.submit_yaml, name='submit_yaml'),
    path('yaml/submit/<slug:yaml_id>', views.submit_yaml, name='submit_yaml'),
    path('yaml/del/<int:yaml_id>/', views.delete_yaml, name="del"),
]