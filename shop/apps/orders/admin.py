from django.contrib import admin
from .models import *


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("clothing_item", "size", "quantity", "price", "cost")
    can_delete = False

    @admin.display(description="Сумма")
    def cost(self, obj):
        return obj.cost

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "full_name",
        "tracking_number",
        "postal_code",
        "status",
        "total_cost",
    )
    list_filter = ("city", "street", "created_at", "updated_at")
    search_fields = (
        "id",
        "city",
        "street",
        "first_name",
        "user__email",
        "tracking_number",
    )
    list_editable = (
        "status",
        "tracking_number",
    )
    readonly_fields = ("created_at", "updated_at", "total_cost")
    date_hierarchy = "created_at"
    inlines = [OrderItemInline]

    @admin.display(description="Покупатель")
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    @admin.display(description="Итог")
    def total_cost(self, obj):
        return obj.total_cost
