from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models


class User(AbstractUser):
    phone = models.CharField("Телефон", max_length=20, blank=True)
    email = models.EmailField("Email", unique=True)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username


class Warehouse(models.Model):
    city = models.CharField("Город", max_length=100)
    address = models.CharField("Адрес", max_length=255)
    temperature = models.CharField(
        "Температура",
        max_length=50,
        default="+18 °С"
    )
    ceiling_height = models.DecimalField(
        "Высота потолков (м)",
        max_digits=4,
        decimal_places=1,
        default=3.5
    )
    advantage = models.CharField(
        "Преимущество (тег)",
        max_length=100,
        blank=True,
        help_text="Например: Рядом с метро, Парковка"
    )
    description = models.TextField("Описание склада", blank=True)
    contacts = models.TextField("Контакты", blank=True)
    directions = models.TextField("Схема проезда", blank=True)
    image = models.ImageField(
        "Фото склада",
        upload_to="warehouses/",
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Склад"
        verbose_name_plural = "Склады"

    def __str__(self):
        return f"{self.city}, {self.address}"


class Box(models.Model):
    STATUS_CHOICES = [
        ("free", "Свободен"),
        ("rented", "Арендован"),
        ("reserved", "Забронирован"),
    ]

    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name="boxes",
        verbose_name="Склад"
    )
    number = models.CharField("Номер бокса", max_length=50)
    floor = models.PositiveIntegerField("Этаж", default=1)
    area = models.DecimalField(
        "Площадь (м²)",
        max_digits=5,
        decimal_places=1
    )
    dimensions = models.CharField(
        "Габариты (Д х Ш х В)",
        max_length=50,
        help_text="Например: 2 х 1.5 х 2.5 м"
    )
    price = models.DecimalField(
        "Цена аренды за месяц (₽)",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    status = models.CharField(
        "Статус",
        max_length=20,
        choices=STATUS_CHOICES,
        default="free"
    )

    class Meta:
        verbose_name = "Бокс"
        verbose_name_plural = "Боксы"

    def __str__(self):
        return f"Бокс {self.number} ({self.warehouse.city}, {self.area} м²)"


class Order(models.Model):
    STATUS_CHOICES = [
        ("active", "Активна"),
        ("expired", "Просрочена"),
        ("closed", "Завершена"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Арендатор"
    )
    box = models.ForeignKey(
        Box,
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name="Бокс"
    )
    start_date = models.DateField("Дата начала аренды")
    end_date = models.DateField("Дата окончания аренды")
    status = models.CharField(
        "Статус аренды",
        max_length=20,
        choices=STATUS_CHOICES,
        default="active"
    )
    qr_code = models.ImageField(
        "QR-код доступа",
        upload_to="qrcodes/",
        blank=True,
        null=True
    )
    access_code = models.CharField(
        "Пин-код замка",
        max_length=20,
        blank=True
    )
    need_delivery = models.BooleanField("Требуется бесплатная доставка", default=False)
    client_address = models.CharField(
        "Адрес для забора вещей",
        max_length=255,
        blank=True
    )
    created_at = models.DateTimeField("Создан", auto_now_add=True)

    class Meta:
        verbose_name = "Заказ аренды"
        verbose_name_plural = "Заказы аренды"

    def __str__(self):
        return f"Заказ #{self.id} — {self.user.username} ({self.box.number})"


class Lead(models.Model):
    email = models.EmailField(
        "E-mail клиента",
        blank=True
    )
    phone = models.CharField(
        "Телефон",
        max_length=20,
        blank=True
    )
    created_at = models.DateTimeField("Дата заявки", auto_now_add=True)
    is_processed = models.BooleanField("Обработано", default=False)

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки с сайта"

    def __str__(self):
        return f"Заявка #{self.id}: {self.email or self.phone}"
