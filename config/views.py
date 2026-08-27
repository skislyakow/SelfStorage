from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = "index.html"


class FaqView(TemplateView):
    template_name = "faq.html"


class StorageRulesView(TemplateView):
    template_name = "storage_rules.html"
