from django.contrib import admin
from django.urls import path, include

from monitor.views import EventListUpdate, EventCountList, RequestList


handler404 = 'monitor.views.error404'

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/events/", EventListUpdate.as_view(), name='event-list-update'),
    path("api/v1/events/count/", EventCountList.as_view(), name='event-count-list'),
    path("api/v1/requests-log/", RequestList.as_view(), name='request-list'),
    path("api/v1/rules/", include('rule.urls')),
]
