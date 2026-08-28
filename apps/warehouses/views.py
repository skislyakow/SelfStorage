from django.db.models import Count, Min, Q
from django.shortcuts import get_object_or_404, render

from apps.warehouses.models import Box, Warehouse


def warehouse_list(request):
    warehouses = Warehouse.objects.annotate(
        total_count=Count("boxes"),
        free_count=Count("boxes", filter=Q(boxes__status="free")),
        min_price=Min(
            "boxes__price_per_month", filter=Q(boxes__status="free")
        ),
    )
    return render(
        request, "warehouses/warehouse_list.html", {"warehouses": warehouses}
    )


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
