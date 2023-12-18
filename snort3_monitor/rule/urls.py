from django.urls import path

from rule.views import RuleCreate, RuleListView


urlpatterns = [
    path("", RuleListView.as_view(), name='rules-list'),
    path("update/", RuleCreate.as_view(), name='rules-create'),
]
