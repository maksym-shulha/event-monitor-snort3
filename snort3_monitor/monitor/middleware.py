from django.utils.deprecation import MiddlewareMixin

from monitor.models import Request


class RequestMiddleware(MiddlewareMixin):
    @staticmethod
    def process_request(request) -> None:
        ip = request.META.get('REMOTE_ADDR', '')
        method = request.method
        filters = request.GET.dict()
        Request.objects.create(user_addr=ip, http_method=method, data=filters)
