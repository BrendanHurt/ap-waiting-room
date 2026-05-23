from django.urls import path

from . import views

app_name = 'users'
urlpatterns = [
    path('login/', views.login_view, name="login"),
    path('validate_auth/', views.validate_auth, name="validate_auth"),
    path('account/', views.account, name='account'),
    path('logout/', views.logout_view, name="logout"),
    path("sign_up/", views.register_form, name="sign_up"),
    path("register/", views.register_user, name="register_user")
]