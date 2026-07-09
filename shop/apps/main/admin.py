from django.contrib import admin
from django.db.models import Count, F, Sum
from django.db.models.functions import Coalesce
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Category, ClothingItem, ClothingItemSize, ItemImage, Size


# ---------------------------------------------------------------------------
# Инлайны
# ---------------------------------------------------------------------------


class ClothingItemSizeInline(admin.TabularInline):
    model = ClothingItemSize
    extra = 1
    min_num = 0
    autocomplete_fields = ("size",)
    fields = ("size", "quantity", "available_display")
    readonly_fields = ("available_display",)

    @admin.display(description=_("В наличии"), boolean=True)
    def available_display(self, obj):
        return obj.available if obj.pk else None


class ItemImageInline(admin.TabularInline):
    model = ItemImage
    extra = 1
    fields = ("image", "image_preview")
    readonly_fields = ("image_preview",)

    @admin.display(description=_("Превью"))
    def image_preview(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" style="max-height: 80px; border-radius: 4px;" />',
                obj.image.url,
            )
        return "—"


# ---------------------------------------------------------------------------
# Фильтры
# ---------------------------------------------------------------------------


class HasDiscountFilter(admin.SimpleListFilter):
    title = _("Скидка")
    parameter_name = "has_discount"

    def lookups(self, request, model_admin):
        return (
            ("yes", _("Со скидкой")),
            ("no", _("Без скидки")),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(discount__gt=0)
        if self.value() == "no":
            return queryset.filter(discount=0)
        return queryset


class StockStatusFilter(admin.SimpleListFilter):
    title = _("Наличие на складе")
    parameter_name = "stock_status"

    def lookups(self, request, model_admin):
        return (
            ("in_stock", _("В наличии")),
            ("out_of_stock", _("Нет в наличии")),
        )

    def queryset(self, request, queryset):
        if self.value() == "in_stock":
            return queryset.filter(total_stock__gt=0)
        if self.value() == "out_of_stock":
            return queryset.filter(total_stock=0)
        return queryset


# ---------------------------------------------------------------------------
# Size
# ---------------------------------------------------------------------------


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ("name", "order")
    list_editable = ("order",)
    search_fields = ("name",)
    ordering = ("order", "name")


# ---------------------------------------------------------------------------
# Category
# ---------------------------------------------------------------------------


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "item_count")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_item_count=Count("clothing_items"))

    @admin.display(description=_("Товаров"), ordering="_item_count")
    def item_count(self, obj):
        return obj._item_count


# ---------------------------------------------------------------------------
# ClothingItem
# ---------------------------------------------------------------------------


@admin.register(ClothingItem)
class ClothingItemAdmin(admin.ModelAdmin):
    list_display = (
        "image_preview",
        "name",
        "category",
        "price",
        "discount",
        "final_price",
        "total_stock",
        "created_at",
    )
    list_display_links = ("image_preview", "name")
    list_editable = ("discount",)
    list_filter = ("category", HasDiscountFilter, StockStatusFilter, "created_at")
    list_select_related = ("category",)
    search_fields = ("name", "slug", "description", "category__name")
    autocomplete_fields = ("category",)
    prepopulated_fields = {"slug": ("name",)}
    date_hierarchy = "created_at"
    readonly_fields = ("final_price", "created_at", "updated_at", "image_preview_large")
    save_on_top = True
    list_per_page = 25
    actions = ("reset_discount",)
    inlines = (ClothingItemSizeInline, ItemImageInline)

    fieldsets = (
        (None, {"fields": ("name", "slug", "category", "description")}),
        (_("Изображение"), {"fields": ("image", "image_preview_large")}),
        (_("Цена"), {"fields": ("price", "discount", "final_price")}),
        (_("Служебная информация"), {"fields": ("created_at", "updated_at")}),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("category")
            .annotate(
                total_stock=Coalesce(Sum("clothingitemsize__quantity"), 0)
            )
        )

    @admin.display(description=_("Итоговая цена"))
    def final_price(self, obj):
        if obj.pk is None or obj.price is None:
            return "—"
        return f"{obj.get_price_with_discount()} ₽"

    @admin.display(description=_("Остаток"), ordering="total_stock")
    def total_stock(self, obj):
        return obj.total_stock

    @admin.display(description=_("Фото"))
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height: 40px; border-radius: 4px;" />',
                obj.image.url,
            )
        return "—"

    @admin.display(description=_("Фото"))
    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 200px; border-radius: 6px;" />',
                obj.image.url,
            )
        return _("Изображение не загружено")

    @admin.action(description=_("Сбросить скидку у выбранных товаров"))
    def reset_discount(self, request, queryset):
        updated = queryset.update(discount=0)
        self.message_user(request, _("Скидка сброшена у %(count)d товаров.") % {"count": updated})


# ---------------------------------------------------------------------------
# ClothingItemSize (отдельный реестр — удобно для поиска/фильтрации по складу)
# ---------------------------------------------------------------------------


@admin.register(ClothingItemSize)
class ClothingItemSizeAdmin(admin.ModelAdmin):
    list_display = ("clothing_item", "size", "quantity", "available")
    list_editable = ("quantity",)
    list_filter = ("size",)
    search_fields = ("clothing_item__name",)
    autocomplete_fields = ("clothing_item", "size")

    @admin.display(description=_("В наличии"), boolean=True)
    def available(self, obj):
        return obj.available


# ---------------------------------------------------------------------------
# ItemImage
# ---------------------------------------------------------------------------


@admin.register(ItemImage)
class ItemImageAdmin(admin.ModelAdmin):
    list_display = ("product", "image_preview")
    search_fields = ("product__name",)
    autocomplete_fields = ("product",)

    @admin.display(description=_("Превью"))
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 80px; border-radius: 4px;" />',
                obj.image.url,
            )
        return "—"
