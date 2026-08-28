from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .services.forms import LoginForm, RegisterForm
from .services.backends import normalize_phone

from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError
from .models import Box, Order, Warehouse, Lead


def index(request):
    if request.method == "POST":
        email = (request.POST.get("EMAIL1") or request.POST.get("EMAIL2") or "").strip()
        phone = (request.POST.get("PHONE1") or request.POST.get("PHONE2") or "").strip()

        if not email and not phone:
            messages.error(request, "Пожалуйста, укажите email или номер телефона.")
            return redirect("self_storage:index")

        try:
            Lead.objects.create(
                email=email,
                phone=phone
            )
            messages.success(request, "Спасибо! Заявка принята, мы свяжемся с вами в ближайшее время.")
        except Exception:
            messages.error(request, "Произошла ошибка при отправке заявки. Попробуйте еще раз.")

        return redirect("self_storage:index")

    return render(request, "index.html")


def boxes(request):
    if request.method == "POST":
        email = request.POST.get("EMAIL1", "").strip()
        phone = request.POST.get("PHONE", "").strip()

        if not email and not phone:
            messages.error(request, "Пожалуйста, укажите email или номер телефона.")
            return redirect("self_storage:boxes")

        try:
            Lead.objects.create(
                email=email,
                phone=phone
            )
            messages.success(request, "Спасибо! Заявка принята, мы свяжемся с вами в ближайшее время.")
        except Exception as e:
            messages.error(request, "Произошла ошибка при отправке заявки. Попробуйте еще раз.")

        return redirect("self_storage:boxes")
    warehouses = Warehouse.objects.all()
    all_boxes = Box.objects.filter(status='free')
    warehouse_filter = request.GET.get('warehouse', '')

    boxes_to3 = all_boxes.filter(area__lte=3)
    boxes_to10 = all_boxes.filter(area__gt=3, area__lte=10)
    boxes_from10 = all_boxes.filter(area__gt=10)

    if warehouse_filter == 'moscow':
        boxes = all_boxes.filter(warehouse__city='Москва')
    elif warehouse_filter == 'odintsovo':
        boxes = all_boxes.filter(warehouse__city='Одинцово')
    elif warehouse_filter == 'pushkino':
        boxes = all_boxes.filter(warehouse__city='Пушкино')
    elif warehouse_filter == 'lubertsi':
        boxes = all_boxes.filter(warehouse__city='Люберцы')
    elif warehouse_filter == 'domodedovo':
        boxes = all_boxes.filter(warehouse__city='Домодедово')
    else:
        boxes = all_boxes

    return render(request, "boxes.html", {
        "boxes": boxes,
        "boxes_to3": boxes_to3,
        "boxes_to10": boxes_to10,
        "boxes_from10": boxes_from10,
        "selected_warehouse": warehouse_filter,
        "warehouses": warehouses,
    })


def faq(request):
    return render(request, "faq.html")


@login_required(login_url="self_storage:index")
def rental_request(request):
    if request.method == 'POST':
        box_id = request.POST.get('box_id', '').strip()
        
        if not box_id:
            messages.error(request, 'Пожалуйста, выберите бокс.')
            return redirect(request.META.get("HTTP_REFERER", "self_storage:boxes"))
        
        try:
            box = Box.objects.get(id=box_id)
        except Box.DoesNotExist:
            messages.error(request, 'Выбранный бокс не найден.')
            return redirect(request.META.get("HTTP_REFERER", "self_storage:boxes"))

        existing_request = Order.objects.filter(
            user=request.user,
            box=box,
            is_rental_request=True
        ).exists()
        
        if existing_request:
            messages.warning(request, f'Вы уже отправили заявку на бокс №{box.number}. Ожидайте звонка менеджера.')
            return redirect(request.META.get("HTTP_REFERER", "self_storage:boxes"))

        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=30)
        
        Order.objects.create(
            user=request.user,
            box=box,
            start_date=start_date,
            end_date=end_date,
            status='active',
            is_rental_request=True,
        )
        
        messages.success(request, f'Заявка на бокс №{box.number} отправлена! Менеджер свяжется с вами для подтверждения.')
        return redirect(request.META.get("HTTP_REFERER", "self_storage:boxes"))
    
    return redirect("self_storage:boxes")


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
