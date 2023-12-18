from django.urls import path

from monitor.views import EventListUpdate, EventCountList

urlpatterns = [
    path("", EventListUpdate.as_view(), name='event-list-update'),
    path("count/", EventCountList.as_view(), name='event-count-list'),
]
