from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal

from apps.main.models import ClothingItem, Size


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"
        CANCELED = "canceled", "Canceled"

    user = models.CharField(max_length=30)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders"
    )
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    middle_name = models.CharField(max_length=30, blank=True)
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=150)
    house_number = models.CharField(max_length=10)
    apartment_number = models.CharField(max_length=10, blank=True)
    postal_code = models.CharField(max_length=10)

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True
    )
    tracking_number = models.CharField(max_length=40, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Order"
        verbose_name_plural = "Order"
        indexes = [models.Index(fields=["created_at"])]

    def __str__(self):
        return f"Order {self.pk} from {self.first_name} {self.last_name}"

    @property
    def total_cost(self) -> Decimal: ...


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    clothing_item = models.ForeignKey(ClothingItem, on_delete=models.PROTECT)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(Decimal("1"))])
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"
        constraints = [
            models.UniqueConstraint(
                fields=["order", "clothing_item", "size"], name="unique_order_item_size"
            ),
        ]

    def __str__(self):
        return f"{self.quantity} x {self.clothing_item} ({self.size})"

    @property
    def cost(self) -> Decimal:
        return self.price * self.quantity
