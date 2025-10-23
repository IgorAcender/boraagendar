from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from tenants.models import Tenant, TenantMembership
from tenants.services import (
    TenantSelectionRequired,
    ensure_membership,
    ensure_membership_for_request,
)

from .forms import SignupForm


def signup_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)

    next_url = request.GET.get("next") or settings.LOGIN_REDIRECT_URL

    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user, tenant = form.save()
            login(request, user)
            request.session["active_tenant_id"] = tenant.id
            redirect_to = request.POST.get("next") or next_url
            return redirect(redirect_to)
    else:
        form = SignupForm()

    return render(request, "accounts/signup.html", {"form": form, "next": next_url})


@login_required
def dashboard_profile_view(request: HttpRequest) -> HttpResponse:
    try:
        membership = ensure_membership_for_request(request)
    except TenantSelectionRequired:
        return redirect(_build_selection_url(request))

    # Handle professional profile update
    from django.contrib import messages
    from scheduling.models import Professional

    professional = None
    try:
        professional = request.user.professional_profile
    except (AttributeError, Professional.DoesNotExist):
        pass

    if request.method == "POST" and professional:
        # Update professional avatar
        if 'avatar' in request.FILES:
            professional.avatar = request.FILES['avatar']
            professional.save()
            messages.success(request, "Foto atualizada com sucesso!")
            return redirect("accounts:profile")

    return render(
        request,
        "accounts/profile.html",
        {"tenant": membership.tenant, "professional": professional},
    )


@login_required
def select_tenant_view(request: HttpRequest) -> HttpResponse:
    next_url = request.GET.get("next") or request.POST.get("next") or settings.LOGIN_REDIRECT_URL
    errors: list[str] = []
    memberships = list(
        TenantMembership.objects.filter(
            user=request.user,
            is_active=True,
            tenant__is_active=True,
        )
        .select_related("tenant")
        .order_by("tenant__name")
    )
    available_tenants = [membership.tenant for membership in memberships]

    if request.user.is_superuser:
        available_tenants = list(Tenant.objects.filter(is_active=True).order_by("name"))

    if request.method == "POST":
        tenant_id_raw = request.POST.get("tenant_id")
        if tenant_id_raw:
            try:
                tenant_id = int(tenant_id_raw)
            except (TypeError, ValueError):
                errors.append("Selecione uma empresa valida.")
            else:
                try:
                    membership = ensure_membership(request.user, tenant_id=tenant_id)
                except (PermissionDenied, TenantSelectionRequired) as exc:
                    errors.append(str(exc))
                else:
                    request.session["active_tenant_id"] = membership.tenant_id
                    return redirect(next_url)
        else:
            errors.append("Selecione uma empresa.")
    else:
        if available_tenants and len(available_tenants) == 1:
            sole_tenant = available_tenants[0]
            request.session["active_tenant_id"] = sole_tenant.id
            return redirect(next_url)

    selected_tenant_id = None
    if request.method == "POST":
        selected_tenant_id = request.POST.get("tenant_id")
    else:
        selected_tenant_id = request.session.get("active_tenant_id")

    context = {
        "memberships": memberships,
        "tenants": available_tenants,
        "errors": errors,
        "next": next_url,
        "is_superuser": request.user.is_superuser,
        "selected_tenant_id": str(selected_tenant_id) if selected_tenant_id is not None else None,
    }

    status = 200
    if not available_tenants:
        status = 403
        if not errors:
            errors.append("Nenhuma empresa disponivel para acessar.")
        context["errors"] = errors

    return render(request, "accounts/select_tenant.html", context, status=status)


def _build_selection_url(request: HttpRequest) -> str:
    select_url = reverse("accounts:select_tenant")
    return f"{select_url}?next={request.get_full_path()}"
