from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from apps.notifications.email import greeting, send_notification

from .forms import CustomUserCreationForm, ProfileForm


def _register_redirect_url(request):
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return reverse("home")


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.pd_consent = True
            user.save(update_fields=["pd_consent"])
            send_notification(
                user,
                "Добро пожаловать в SelfStorage",
                f"{greeting(user)}\n\n"
                "Спасибо за регистрацию в SelfStorage. Теперь вы можете подбирать "
                "боксы на карте, оформлять заказы и управлять ими из "
                "личного кабинета.\n\n"
                "С уважением,\nкоманда SelfStorage.",
            )
            login(request, user)
            messages.success(request, "Регистрация прошла успешно!")
            return redirect(_register_redirect_url(request))
    else:
        form = CustomUserCreationForm()

    return render(request, "registration/register.html", {"form": form})


@login_required
@require_POST
def profile(request):
    form = ProfileForm(request.POST, request.FILES, instance=request.user)
    if form.is_valid():
        form.save()
        messages.success(request, "Профиль сохранён")
    else:
        for field, error_list in form.errors.items():
            label = form.fields[field].label if field in form.fields else "Форма"
            messages.error(request, f"{label}: {error_list[0]}")
    return redirect("my_rent")
