from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .services.forms import LoginForm, RegisterForm
from .services.backends import normalize_phone


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
    user = request.user

    if request.method == "POST":
        if "first_name" in request.POST:
            user.first_name = request.POST.get("first_name", "").strip()
        if "phone" in request.POST:
            raw_phone = request.POST.get("phone", "").strip()
            if raw_phone:
                try:
                    user.phone = normalize_phone(raw_phone)
                except ValidationError as e:
                    messages.error(request, e.message)
                    return redirect("self_storage:my_rent")
            else:
                user.phone = ""

        if "avatar" in request.FILES:
            user.avatar = request.FILES["avatar"]
        user.save()
        messages.success(request, "Данные профиля успешно обновлены!")
        return redirect("self_storage:my_rent")
    user_orders = (
        user.orders.select_related("box", "box__warehouse")
        .order_by("-created_at")
    )
    template_name = "my-rent.html" if user_orders.exists() else "my-rent-empty.html"

    return render(
        request,
        template_name,
        {
            "user": user,
            "orders": user_orders,
        },
    )
