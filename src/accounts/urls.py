from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from .views import dashboard_profile_view, select_tenant_view

app_name = "accounts"

urlpatterns = [
    path(
        "login/",
        LoginView.as_view(
            template_name="accounts/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path(
        "logout/",
        LogoutView.as_view(),
        name="logout",
    ),
    path("selecionar-empresa/", select_tenant_view, name="select_tenant"),
    path("perfil/", dashboard_profile_view, name="profile"),
]
