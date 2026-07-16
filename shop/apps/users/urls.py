from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = "users"

urlpatterns = [
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("register/", views.RegisterView.as_view(), name="register"),
    # path("profile/", views.profile, name="profile"),
    path("logout/", LogoutView.as_view(next_page="users:login"), name="logout"),
]
