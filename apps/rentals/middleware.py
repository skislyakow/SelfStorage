from django.utils.deprecation import MiddlewareMixin


class TrafficSourceMiddleware(MiddlewareMixin):
    SOURCE_PARAMS = ("utm_source", "src")

    def process_request(self, request):
        for param in self.SOURCE_PARAMS:
            value = request.GET.get(param)
            if value:
                request.session["traffic_source"] = value
                break
        return None
