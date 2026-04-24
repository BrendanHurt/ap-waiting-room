from django.urls import path

from . import views

app_name = 'users'
urlpatterns = [
    path('login/', views.login, name="login"),
    path('<int:user_id>/account/', views.account, name='account'),
    path('logout/', views.logout, name="logout"),
    path("sign_up/", views.register_form, name="sign_up"),
    path("register/", views.register_user, name="register_user")
]