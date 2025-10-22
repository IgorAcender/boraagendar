from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from .forms import EmailAuthenticationForm
from .views import dashboard_profile_view, select_tenant_view, signup_view

app_name = "accounts"

urlpatterns = [
    path("signup/", signup_view, name="signup"),
    path(
        "login/",
        LoginView.as_view(
            template_name="accounts/login.html",
            redirect_authenticated_user=True,
            authentication_form=EmailAuthenticationForm,
        ),
        name="login",
    ),
    path(
        "logout/",
        LogoutView.as_view(next_page="accounts:login"),
        name="logout",
    ),
    path("selecionar-empresa/", select_tenant_view, name="select_tenant"),
    path("perfil/", dashboard_profile_view, name="profile"),
]
