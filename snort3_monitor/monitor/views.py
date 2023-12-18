from datetime import datetime, timedelta

from django.db.models import Count, Value
from django.db.models.functions import Concat
from django.db.models import F
from django.db.models.query import QuerySet
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import Event
from .serializers import EventSerializer, EventCountAddressSerializer, EventCountRuleSerializer


class EventListUpdate(generics.UpdateAPIView, generics.ListAPIView):
    queryset = Event.objects.filter(mark_as_deleted=False)
    serializer_class = EventSerializer

    def get_queryset(self) -> QuerySet:
        """Perform filtering and ordering data

        Client can use only allowed_params in query.
        """
        allowed_params = ['src_addr', 'src_port', 'dst_addr', 'dst_port', 'sid', 'proto']
        queryset = super().get_queryset()

        # if method=PATCH, we don't need to process queries
        if self.request.method == 'PATCH':
            return queryset

        params = self.request.query_params
        params = {key: value for key, value in params.items()}
        if params:
            validate_params(params.keys(), allowed_params)

            # changing sid key
            if params.get('sid') is not None:
                params['rule__sid'] = params.pop('sid')

            if params.get('page') is not None:
                params.pop('page')

            queryset = queryset.filter(**params)
        return queryset.order_by('id')

    def patch(self, request, *args, **kwargs) -> Response:
        """Mark all events as deleted to ide them"""
        queryset = self.get_queryset()
        queryset.update(mark_as_deleted=True)
        return Response({"message": "All events are marked as deleted."}, status=status.HTTP_200_OK)


class EventCountList(generics.ListAPIView):
    queryset = Event.objects.filter(mark_as_deleted=False)

    def get_queryset(self) -> QuerySet:
        """Perform filtering and ordering data

        Client can use only allowed_params in query.
        """
        queryset = Event.objects.all()
        periods = {
            'all': None,
            'day': timedelta(days=1),
            'week': timedelta(days=7),
            'month': timedelta(days=30)
        }

        allowed_params = ['type', 'period']
        params = self.request.query_params
        params = {key: value for key, value in params.items()}

        # check existing type parameter
        if params.get('type') is None:
            raise ValidationError({"error": "You should define 'type' of filter (sid or addr)"})

        validate_params(params.keys(), allowed_params)

        # check if period is known and filter it
        if params.get('period') is not None:
            if periods.get(params.get('period')) is not None:
                period_start = datetime.now() - periods[params.get('period')]
                queryset = queryset.filter(timestamp__gte=period_start)
            else:
                if params.get('period') != 'all':
                    raise ValidationError({"error": "Unknown 'period', use 'all', 'day', 'week' or 'month'"})

        # aggregation
        if params.get('type') == 'addr':
            EventCountList.serializer_class = EventCountAddressSerializer
            queryset = (
                queryset
                .annotate(addr_pair=Concat('src_addr', Value('/'), 'dst_addr'))
                .values('addr_pair')
                .annotate(count=Count('addr_pair'))
            )
        elif params.get('type') == 'sid':
            EventCountList.serializer_class = EventCountRuleSerializer
            queryset = (
                queryset
                .values(sid=F('rule__sid'))
                .annotate(count=Count('rule__sid'))
            )
        else:
            raise ValidationError(
                {"error": "Unknown 'type', use 'sid' or 'addr'"})

        return queryset.order_by('count')


def error404(request, exception):
    """Default 404 response"""
    return Response({"error": "The request is malformed or invalid."}, status=status.HTTP_404_NOT_FOUND)


def validate_params(entered, allowed: list) -> None:
    """Validate query parameters

    :param entered: Params of query, which user entered
    :param allowed: Params that are allowed in endpoint
    """
    allowed.append('page')
    only_allowed_params_present = set(entered).issubset(set(allowed))
    if not only_allowed_params_present:
        raise ValidationError(
            {"error": f"You can use only {', '.join(allowed)} as query filters."})
