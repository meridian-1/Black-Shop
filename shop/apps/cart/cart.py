from decimal import Decimal
from typing import Iterator, TypedDict

from django.conf import settings
from django.http import HttpRequest

from apps.main.models import ClothingItem, ClothingItemSize


class CartRow(TypedDict):
    item: ClothingItem
    size: str
    quantity: int
    price: Decimal
    total_price: Decimal


class Cart:
    def __init__(self, request: HttpRequest) -> None:
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if cart is None:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart: dict[str, dict[str, int]] = cart

    @staticmethod
    def _make_key(item_id: int | str, size: str) -> str:
        return f"{item_id}:{size}"

    @staticmethod
    def _stock_for(clothing_item: ClothingItem, size: str) -> int:
        """the quantity of this product in the database"""
        stock = (
            ClothingItemSize.objects
            .filter(clothing_item=clothing_item, size__name=size)
            .values_list("quantity", flat=True)
            .first()
        )
        return stock or 0

    def save(self) -> None:
        self.session.modified = True

    def add(
        self,
        clothing_item: ClothingItem,
        size: str,
        quantity: int = 1,
        override_quantity: bool = False,
    ) -> None:
        """
        Add an item or change the quantity
        """
        key = self._make_key(clothing_item.id, size)
        row = self.cart.setdefault(key, {"quantity": 0})

        if override_quantity:
            row["quantity"] = quantity
        else:
            row["quantity"] += quantity

        row["quantity"] = min(row["quantity"], self._stock_for(clothing_item, size))

        if row["quantity"] <= 0:
            del self.cart[key]

        self.save()

    def remove(self, clothing_item: ClothingItem, size: str) -> None:
        """delete an item"""
        key = self._make_key(clothing_item.id, size)
        if key in self.cart:
            del self.cart[key]
            self.save()

    def clear(self) -> None:
        """clear cart"""
        self.session.pop(settings.CART_SESSION_ID, None)
        self.save()

    def __iter__(self) -> Iterator[CartRow]:
        """for iteration in the template"""
        item_ids = {key.partition(":")[0] for key in self.cart}
        items = ClothingItem.objects.filter(id__in=item_ids).in_bulk()

        for key, row in self.cart.items():
            item_id, _, size = key.partition(":")
            item = items.get(int(item_id))
            if item is None:
                continue

            price = item.get_price_with_discount()
            yield CartRow(
                item=item,
                size=size,
                quantity=row["quantity"],
                price=price,
                total_price=price * row["quantity"],
            )

    def __len__(self) -> int:
        """total number of products {{ cart|length }} и len(cart)"""
        return sum(row["quantity"] for row in self.cart.values())

    def get_total_price(self) -> Decimal:
        return sum((row["total_price"] for row in self), Decimal("0"))
    