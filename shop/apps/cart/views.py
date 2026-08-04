from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.main.models import ClothingItem, ClothingItemSize, Size
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
        try:
            size_object = Size.objects.get(name=size)
            clothing_item_size = ClothingItemSize.objects.get(
                clothing_item=clothing_item, size=size_object
            )

            if clothing_item_size.quantity <= 0:
                return redirect("cart:cart_detail")
        except (Size.DoesNotExist, ClothingItemSize.DoesNotExist):
            return redirect("cart:cart_detail")
    else:
        available_sizes = clothing_item.sizes.filter(clothingitemsize__quantity__gt=0)
        if available_sizes.exists():
            size_object = available_sizes.first()
            size = size_object.name
        else:
            return redirect("cart:cart_detail")

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
