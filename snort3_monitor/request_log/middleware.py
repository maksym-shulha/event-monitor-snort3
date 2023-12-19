from request_log.models import Request


class RequestMiddleware:
    """Responsible for logging client's requests to data base"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = request.META.get('REMOTE_ADDR', '')
        method = request.method
        filters = request.GET.dict()
        endpoint = request.META.get('PATH_INFO', '')

        response = self.get_response(request)

        Request.objects.create(
            user_addr=ip,
            http_method=method,
            request_data=filters,
            response=response.status_code,
            endpoint=endpoint
        )

        return response
