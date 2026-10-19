from collections.abc import Callable

from django.http import HttpRequest, HttpResponseBase

# Content-Security-Policy: откуда страница может грузить ресурсы.
# Инлайн-скриптов в шаблонах нет — свой JS вынесен в static/js, поэтому
# script-src строгий ('self' + CDN, откуда берётся Bootstrap). 'unsafe-inline'
# в style-src нужен под инлайн-атрибуты style= и <style> в админке: на защиту
# от XSS влияет script-src, а не стили.
CONTENT_SECURITY_POLICY = "; ".join(
    [
        "default-src 'self'",
        "script-src 'self' https://cdn.jsdelivr.net",
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net"
        " https://fonts.googleapis.com",
        "font-src 'self' https://fonts.gstatic.com",
        # data: — SVG-фоны чекбоксов и стрелки select из Bootstrap.
        "img-src 'self' data:",
        "connect-src 'self'",
        "frame-src https://www.youtube.com",
        "frame-ancestors 'none'",
        "base-uri 'self'",
        "form-action 'self'",
        "object-src 'none'",
    ]
)


class ContentSecurityPolicyMiddleware:
    """Ставит Content-Security-Policy на каждый ответ приложения."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponseBase]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponseBase:
        response = self.get_response(request)
        response.headers.setdefault("Content-Security-Policy", CONTENT_SECURITY_POLICY)
        return response
