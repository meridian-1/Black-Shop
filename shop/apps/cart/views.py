from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.main.models import ClothingItem
from .cart import Cart


def _parse_quantity(raw, default=1):
    try:
        quantity = int(raw)
    except (TypeError, ValueError):
        return default
    return max(quantity, 1)


def cart_detail(request):
    cart = Cart(request)
    return render(request, "cart_detail.html", {"cart": cart})


@require_POST
def cart_add(request, item_id):
    cart = Cart(request)
    clothing_item = get_object_or_404(ClothingItem, id=item_id)
    size = request.POST.get("size")
    quantity = _parse_quantity(request.POST.get("quantity"))
    if size:
        cart.add(clothing_item, size, quantity)
    # return redirect("main:clothing_item_detail", clothing_item.slug)
    return HttpResponse(status=204)


@require_POST
def cart_update(request, item_id, size):
    cart = Cart(request)
    clothing_item = get_object_or_404(ClothingItem, id=item_id)
    quantity = _parse_quantity(request.POST.get("quantity"))
    cart.add(clothing_item, size, quantity, override_quantity=True)
    return redirect("cart:cart_detail")


@require_POST
def cart_remove(request, item_id, size):
    cart = Cart(request)
    clothing_item = get_object_or_404(ClothingItem, id=item_id)
    cart.remove(clothing_item, size)
    return render(request, "includes/cart_total.html", {"cart": cart})
