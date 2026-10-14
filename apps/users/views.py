from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render

from apps.notifications.email import greeting, send_notification

from .forms import CustomUserCreationForm


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
            return redirect("home")
    else:
        form = CustomUserCreationForm()

    return render(request, "registration/register.html", {"form": form})
