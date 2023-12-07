from datetime import datetime, timedelta

from django.db.models import Count, Value
from django.db.models.functions import Concat
from django.http import HttpResponseNotFound
from django.db.models import F
from django.db.models.query import QuerySet
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import Event
from .serializers import EventSerializer, EventCountAddressSerializer, EventCountRuleSerializer


class EventListUpdate(generics.UpdateAPIView, generics.ListAPIView):
    queryset = Event.objects.filter(mark_as_deleted=False)
    serializer_class = EventSerializer

    def get_queryset(self) -> QuerySet:
        allowed_params = ['src_addr', 'src_port', 'dst_addr', 'dst_port', 'sid', 'proto']
        queryset = super().get_queryset()

        # if method=PATCH, we don't need to process queries
        if self.request.method == 'PATCH':
            return queryset

        params = self.request.query_params
        params = {key: value for key, value in params.items()}
        if params:
            # Checking if all params are allowed
            only_allowed_params_present = set(params.keys()).issubset(set(allowed_params))
            if not only_allowed_params_present:
                raise ValidationError(
                    {"error": "You can use only 'src_addr', 'src_port', 'dst_addr', 'dst_port', "
                              "'sid' and 'proto' to filter events"})
            # changing sid key
            if params.get('sid'):
                params['rule__sid'] = params.pop('sid')

            queryset = queryset.filter(**params)
        return queryset

    def patch(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset.update(mark_as_deleted=True)
        return Response({"message": "All events are marked as deleted."})


class EventCountList(generics.ListAPIView):
    queryset = Event.objects.filter(mark_as_deleted=False)

    def get_queryset(self) -> QuerySet:
        queryset = super().get_queryset()
        periods = {
            'all': None,
            'day': timedelta(days=1),
            'week': timedelta(days=7),
            'month': timedelta(days=30)
        }

        type_of_filter = self.request.query_params.get('type')
        period = self.request.query_params.get('period')

        # checking if all params are included
        if not (type_of_filter and period):
            raise ValidationError(
                {"error": "You should define 'type' of filter (sid or addr) and 'period' (all, day, week, month)"})

        # checking if period is known
        if periods.get(period):
            period_start = datetime.now() - periods[period]
            queryset = queryset.filter(timestamp__gte=period_start)
        else:
            if period != 'all':
                raise ValidationError({"error": "Unknown 'period', use 'all', 'day', 'week' or 'month'"})

        # aggregation
        if type_of_filter == 'addr':
            EventCountList.serializer_class = EventCountAddressSerializer
            queryset = queryset.annotate(addr_pair=Concat('src_addr', Value('/'), 'dst_addr')
                                         ).values('addr_pair').annotate(count=Count('addr_pair'))
        elif type_of_filter == 'sid':
            EventCountList.serializer_class = EventCountRuleSerializer
            queryset = queryset.values(sid=F('rule__sid')).annotate(count=Count('rule__sid'))
        else:
            raise ValidationError(
                {"error": "Unknown 'type', use 'sid' or 'addr'"})

        return queryset


def error404(request, exception):
    """
    default 404 response
    need DEBUG=False
    """
    return HttpResponseNotFound('{"error": "The request is malformed or invalid."}')
