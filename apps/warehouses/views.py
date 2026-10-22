from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Min, Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.warehouses.models import Box, Warehouse

from .forms import ReviewForm


def warehouse_list(request):
    warehouses = Warehouse.objects.annotate(
        total_count=Count("boxes"),
        free_count=Count("boxes", filter=Q(boxes__status="free")),
        min_price=Min("boxes__price_per_month", filter=Q(boxes__status="free")),
    )
    return render(request, "warehouses/warehouse_list.html", {"warehouses": warehouses})


def warehouse_detail(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    boxes = Box.objects.filter(warehouse=warehouse, status="free")

    filters = {}
    floor = request.GET.get("floor")
    if floor:
        try:
            value = int(floor)
            boxes = boxes.filter(floor=value)
            filters["floor"] = value
        except ValueError:
            pass

    ranges = (
        ("min_area", "area__gte"),
        ("max_area", "area__lte"),
        ("min_price", "price_per_month__gte"),
        ("max_price", "price_per_month__lte"),
    )
    for param, field in ranges:
        raw = request.GET.get(param)
        if raw:
            try:
                value = float(raw)
                boxes = boxes.filter(**{field: value})
                filters[param] = value
            except ValueError:
                pass

    return render(
        request,
        "warehouses/warehouse_detail.html",
        {"warehouse": warehouse, "boxes": boxes, "filters": filters},
    )


@login_required
def review_create(request):
    if request.method == "POST":
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.author_name = request.user.first_name or request.user.email
            review.is_published = False
            review.save()
            messages.success(
                request, "Спасибо! Отзыв появится на сайте после проверки."
            )
            return redirect("home")
    else:
        form = ReviewForm()
    return render(request, "warehouses/review_form.html", {"form": form})
