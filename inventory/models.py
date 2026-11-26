from django.conf import settings
from django.db import models
from django.db.models import Q


class Category(models.Model):
    business = models.ForeignKey(
        "accounts.Business", on_delete=models.CASCADE, related_name="categories"
    )
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["business", "name"], name="unique_category_per_business"
            )
        ]

    def __str__(self):
        return self.name


class Product(models.Model):
    business = models.ForeignKey(
        "accounts.Business", on_delete=models.CASCADE, related_name="products"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    name = models.CharField(max_length=150)
    sku = models.CharField(max_length=50, blank=True)
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2)
    stock_quantity = models.IntegerField(default=0)
    low_stock_level = models.PositiveIntegerField(default=5)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.CheckConstraint(
                condition=Q(stock_quantity__gte=0), name="stock_never_negative"
            )
        ]

    def __str__(self):
        return self.name

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.low_stock_level


class StockMovement(models.Model):
    class Reason(models.TextChoices):
        OPENING = "opening", "Opening stock"
        RESTOCK = "restock", "Restock"
        SALE = "sale", "Sale"
        RETURN = "return", "Customer return"
        DAMAGE = "damage", "Damaged or lost"
        ADJUSTMENT = "adjustment", "Adjustment"

    business = models.ForeignKey(
        "accounts.Business", on_delete=models.CASCADE, related_name="stock_movements"
    )
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="movements"
    )
    change = models.IntegerField()
    reason = models.CharField(max_length=20, choices=Reason.choices)
    note = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product} {self.change:+d} ({self.reason})"
    