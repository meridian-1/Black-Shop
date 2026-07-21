from decimal import Decimal

from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Size(models.Model):
    name = models.CharField(max_length=10, unique=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["name"])]
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def get_item_count(self):
        return self.clothing_items.count()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ClothingItem(TimeStampedModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="clothing_items"
    )
    sizes = models.ManyToManyField(
        Size, through="ClothingItemSize", related_name="clothing_item", blank=True
    )
    image = models.ImageField(upload_to="product/%Y/%m/%d", blank=True)
    description = models.TextField(max_length=255, blank=True)
    price = models.DecimalField(
        max_digits=20, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0"),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )

    class Meta:
        ordering = [
            "-created_at",
        ]
        indexes = [models.Index(fields=["price"]), models.Index(fields=["slug"])]
        constraints = [
            models.CheckConstraint(
                condition=(models.Q(discount__gte=0) & models.Q(discount__lte=100)),
                name="discount_between_0_and_100",
            ),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_price_with_discount(self):
        if self.discount:
            return round(self.price * (1 - (self.discount / 100)), 2)
        return round(self.price, 2)


class ClothingItemSize(models.Model):
    clothing_item = models.ForeignKey(ClothingItem, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["clothing_item", "size"], name="unique_clothingitem_size"
            )
        ]

    @property
    def available(self) -> bool:
        return self.quantity > 0


class ItemImage(models.Model):
    product = models.ForeignKey(
        ClothingItem, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="product/%Y/%m/%d", blank=True)

    def __str__(self):
        return f"{self.product.name} - {self.image.name}"
