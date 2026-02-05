from django.urls import path

from . import views

app_name = 'users'
urlpatterns = [
    path('', views.index, name='index'),
    path('auth/', views.user_auth, name="user_auth"),
    path('<int:user_id>/account/', views.account, name='account'),
    path('logout/', views.logout, name="logout")
]