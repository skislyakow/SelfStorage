from django.views.generic import TemplateView

from apps.warehouses.models import Review


class HomeView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["reviews"] = Review.objects.filter(is_published=True)
        return context


class FaqView(TemplateView):
    template_name = "faq.html"


class StorageRulesView(TemplateView):
    template_name = "storage_rules.html"


class PrivacyView(TemplateView):
    template_name = "privacy.html"
