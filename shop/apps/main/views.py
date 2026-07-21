from decimal import Decimal, InvalidOperation

from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from .models import Category, ClothingItem, Size, ClothingItemSize


def _parse_decimal(value):
    if not value:
        return None
    try:
        return Decimal(value)
    except (InvalidOperation, ValueError):
        return None


def catalog(request):
    categories = Category.objects.annotate(item_count=Count("clothing_items"))
    sizes = Size.objects.all()

    clothing_items = ClothingItem.objects.select_related("category").prefetch_related(
        "sizes"
    )

    selected_categories = request.GET.getlist("category")
    if selected_categories:
        clothing_items = clothing_items.filter(category__slug__in=selected_categories)

    selected_sizes = request.GET.getlist("size")
    if selected_sizes:
        clothing_items = clothing_items.filter(
            sizes__name__in=selected_sizes
        ).distinct()

    min_price = _parse_decimal(request.GET.get("min_price"))
    if min_price is not None:
        clothing_items = clothing_items.filter(price__gte=min_price)

    max_price = _parse_decimal(request.GET.get("max_price"))
    if max_price is not None:
        clothing_items = clothing_items.filter(price__lte=max_price)

    context = {
        "categories": categories,
        "sizes": sizes,
        "clothing_items": clothing_items,
        "selected_categories": selected_categories,
        "selected_sizes": selected_sizes,
    }

    if request.headers.get("HX-Request"):
        return render(request, "product/includes/card_results.html", context)

    return render(request, "product/list.html", context, using="jinja2")


def clothing_item_detail(request, slug):
    clothing_item = get_object_or_404(
        ClothingItem.objects.select_related("category").prefetch_related("images"),
        slug=slug,
    )

    available_sizes = (
        ClothingItemSize.objects.filter(quantity__gt=0)
        .select_related("size")
        .order_by("size__order", "size__name")
    )

    context = {
        "clothing_item": clothing_item,
        "available_sizes": available_sizes,
    }

    return render(request, "product/detail.html", context)
