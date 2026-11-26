from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import redirect, render

from accounts.decorators import owner_required

from .forms import ProductForm
from .models import Product, StockMovement
from .services import change_stock


@login_required
def product_list(request):
    products = Product.objects.filter(
        business=request.user.business, is_active=True
    ).select_related("category")
    q = request.GET.get("q", "").strip()
    if q:
        products = products.filter(Q(name__icontains=q) | Q(sku__icontains=q))
    return render(request, "inventory/product_list.html", {"products": products, "q": q})


@owner_required
def product_create(request):
    business = request.user.business
    if request.method == "POST":
        form = ProductForm(request.POST, business=business)
        if form.is_valid():
            with transaction.atomic():
                product = form.save(commit=False)
                product.business = business
                product.save()
                opening = form.cleaned_data.get("opening_stock") or 0
                if opening > 0:
                    change_stock(
                        product_id=product.id,
                        business=business,
                        change=opening,
                        reason=StockMovement.Reason.OPENING,
                        user=request.user,
                    )
            return redirect("product_list")
    else:
        form = ProductForm(business=business)
    return render(request, "inventory/product_form.html", {"form": form})
