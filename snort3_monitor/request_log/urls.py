from django.urls import path

from request_log.views import RequestList


urlpatterns = [
    path("", RequestList.as_view(), name='request-list'),
]
