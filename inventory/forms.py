from django import forms

from .models import Category, Product


class ProductForm(forms.ModelForm):
    opening_stock = forms.IntegerField(
        min_value=0, initial=0, required=False, label="Opening stock"
    )

    class Meta:
        model = Product
        fields = [
            "name", "category", "sku",
            "cost_price", "selling_price", "low_stock_level",
        ]
        labels = {
            "sku": "Product code (optional)",
            "cost_price": "Cost price",
            "selling_price": "Selling price",
            "low_stock_level": "Warn me when stock reaches",
        }

    def __init__(self, *args, business, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = Category.objects.filter(business=business)

    def clean(self):
        cleaned = super().clean()
        for name in ("cost_price", "selling_price"):
            value = cleaned.get(name)
            if value is not None and value < 0:
                self.add_error(name, "Must be zero or more.")
        return cleaned

class StockAdjustForm(forms.Form):
    reason = forms.ChoiceField(
        choices=[
            ("restock", "Restock (stock in)"),
            ("damage", "Damaged or lost (stock out)"),
        ],
        label="What happened?",
    )
    quantity = forms.IntegerField(min_value=1, label="Quantity")
    note = forms.CharField(max_length=255, required=False, label="Note (optional)")
