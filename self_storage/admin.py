from django.contrib import admin
from .models import Warehouse, Box, Order, Lead


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = (
        "city",
        "address",
        "temperature",
        "ceiling_height",
        "advantage"
    )
    search_fields = ("city", "address")


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = (
        "number",
        "warehouse",
        "floor",
        "area",
        "price",
        "status"
    )
    list_filter = (
        "status",
        "warehouse",
        "floor"
    )
    search_fields = ("number",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "box",
        "start_date",
        "end_date",
        "status",
        "need_delivery"
    )
    list_filter = (
        "status",
        "need_delivery",
        "start_date",
        "end_date"
    )
    search_fields = (
        "user__username",
        "user__email",
        "box__number",
        "client_address"
    )


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "email",
        "phone",
        "created_at",
        "is_processed"
    )
    list_filter = ("is_processed", "created_at")
    search_fields = ("email", "phone")
