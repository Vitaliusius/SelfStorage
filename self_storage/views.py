from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .services.forms import LoginForm, RegisterForm


def index(request):
    return render(request, "index.html")


def boxes(request):
    return render(request, "boxes.html")


def faq(request):
    return render(request, "faq.html")


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            login(request, form.user)
            return redirect("self_storage:my_rent")
        else:
            for errors in form.errors.values():
                for error in errors:
                    messages.error(request, error)
    return redirect(request.META.get("HTTP_REFERER", "self_storage:index"))


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(
                request,
                user,
                backend="self_storage.services.backends.EmailOrUsernameModelBackend",
            )
            messages.success(request, "Регистрация прошла успешно!")
            return redirect("self_storage:my_rent")
        else:
            for errors in form.errors.values():
                for error in errors:
                    messages.error(request, error)
    return redirect(request.META.get("HTTP_REFERER", "self_storage:index"))


def logout_view(request):
    logout(request)
    return redirect("self_storage:index")


@login_required(login_url="self_storage:index")
def my_rent(request):
    user_orders = (
        request.user.orders.select_related("box", "box__warehouse")
        .order_by("-created_at")
    )

    if not user_orders.exists():
        return render(request, "my-rent-empty.html", {"user": request.user})

    return render(
        request,
        "my-rent.html",
        {
            "user": request.user,
            "orders": user_orders,
        },
    )
