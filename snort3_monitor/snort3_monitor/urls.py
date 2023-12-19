from django.contrib import admin
from django.urls import path, include


handler404 = 'monitor.views.error404'

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/events/", include('monitor.urls')),
    path("api/v1/requests-log/", include('request_log.urls')),
    path("api/v1/rules/", include('rule.urls')),
]
