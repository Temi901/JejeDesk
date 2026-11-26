from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import owner_required

from .forms import ProductForm, StockAdjustForm
from .models import Product, StockMovement
from .services import InsufficientStock, change_stock


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


@login_required
def product_detail(request, pk):
    user = request.user
    product = get_object_or_404(Product, pk=pk, business=user.business)
    is_owner = user.role == user.Role.OWNER
    if request.method == "POST":
        if not is_owner:
            raise PermissionDenied
        form = StockAdjustForm(request.POST)
        if form.is_valid():
            qty = form.cleaned_data["quantity"]
            reason = form.cleaned_data["reason"]
            change = qty if reason == StockMovement.Reason.RESTOCK else -qty
            try:
                change_stock(
                    product_id=product.id,
                    business=user.business,
                    change=change,
                    reason=reason,
                    user=user,
                    note=form.cleaned_data["note"],
                )
            except InsufficientStock as error:
                form.add_error("quantity", str(error))
            else:
                return redirect("product_detail", pk=product.id)
    else:
        form = StockAdjustForm()
    movements = product.movements.select_related("created_by")[:50]
    return render(
        request,
        "inventory/product_detail.html",
        {"product": product, "form": form, "movements": movements, "is_owner": is_owner},
    )
