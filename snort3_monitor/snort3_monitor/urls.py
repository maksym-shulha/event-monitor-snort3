from django.contrib import admin
from django.urls import path

from monitor.views import EventListUpdate, EventCountList


handler404 = 'monitor.views.error404'

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/events/", EventListUpdate.as_view(), name='event-list-update'),
    path("api/v1/events/count/", EventCountList.as_view(), name='event-count-list'),
]
