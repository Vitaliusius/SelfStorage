from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Box, Lead, Order, User, Warehouse, ShortLink
from django.utils.html import format_html


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "email",
        "phone",
        "is_staff",
        "is_active",
    )
    search_fields = ("username", "email", "phone")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Дополнительная информация", {"fields": ("phone",)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Дополнительная информация", {"fields": ("phone",)}),
    )


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = (
        "city",
        "address",
        "temperature",
        "ceiling_height",
        "advantage",
    )
    list_filter = ("city",)
    search_fields = ("city", "address")


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = (
        "number",
        "warehouse",
        "floor",
        "area",
        "price",
        "status",
    )
    list_filter = (
        "status",
        "warehouse",
        "floor",
    )
    search_fields = ("number", "warehouse__address")
    list_editable = ("status", "price")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "box",
        "start_date",
        "end_date",
        "access_code",
        "status",
        "is_rental_request",
        "need_delivery",
        "created_at",
    )
    list_filter = (
        "status",
        "is_rental_request",
        "need_delivery",
        "start_date",
        "end_date",
    )
    search_fields = (
        "user__username",
        "user__email",
        "user__phone",
        "box__number",
        "client_address",
    )
    readonly_fields = ("created_at", "qr_code_preview")
    list_editable = ("status",)

    def qr_code_preview(self, obj):
        if obj.qr_code:
            return format_html(
                '<img src="{}" style="max-height: 120px; border-radius: 6px;" />',
                obj.qr_code.url,
            )
        return "QR-код не сформирован"

    qr_code_preview.short_description = "Превью QR-кода"


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "email",
        "phone",
        "created_at",
        "is_processed",
    )
    list_filter = ("is_processed", "created_at")
    search_fields = ("email", "phone")
    list_editable = ("is_processed",)
    readonly_fields = ("created_at",)


@admin.register(ShortLink)
class ShortLinkAdmin(admin.ModelAdmin):
    list_display = ('short_code', 'original_url', 'display_short_url', 'clicks', 'created_at')
    fields = ('original_url', 'short_code', 'clicks', 'display_short_url')
    readonly_fields = ('clicks', 'display_short_url')

    @admin.display(description="Готовая короткая ссылка")
    def display_short_url(self, obj):
        if obj.id:
            url = obj.get_short_url()
            return format_html('<a href="{0}" target="_blank">{0}</a>', url)
        return "Появится после сохранения"