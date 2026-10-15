from django.contrib import admin

from .models import Box, Review, Warehouse


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author_name",
        "city",
        "warehouse",
        "is_published",
        "created_at",
    )
    list_filter = ("is_published", "warehouse")
    search_fields = ("title", "author_name", "city", "text")
    actions = ("publish", "unpublish")

    @admin.action(description="Опубликовать выбранные отзывы")
    def publish(self, request, queryset):
        updated = queryset.update(is_published=True)
        self.message_user(request, f"Опубликовано отзывов: {updated}")

    @admin.action(description="Снять с публикации выбранные отзывы")
    def unpublish(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, f"Снято с публикации отзывов: {updated}")


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = ("warehouse", "number", "area", "price_per_month", "status")
    list_filter = ("status",)
    search_fields = ("number", "warehouse__city", "warehouse__address")


admin.site.register(Warehouse)
