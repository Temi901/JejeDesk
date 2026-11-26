from django.db import transaction

from .models import Product, StockMovement


class InsufficientStock(Exception):
    pass


def change_stock(*, product_id, business, change, reason, user=None, note=""):
    """Change a product's stock and record the movement, all or nothing."""
    if change == 0:
        raise ValueError("Stock change cannot be zero.")
    with transaction.atomic():
        product = Product.objects.select_for_update().get(
            pk=product_id, business=business
        )
        new_quantity = product.stock_quantity + change
        if new_quantity < 0:
            raise InsufficientStock(
                f"Only {product.stock_quantity} of {product.name} in stock."
            )
        product.stock_quantity = new_quantity
        product.save(update_fields=["stock_quantity", "updated_at"])
        return StockMovement.objects.create(
            business=business,
            product=product,
            change=change,
            reason=reason,
            note=note,
            created_by=user,
        )
