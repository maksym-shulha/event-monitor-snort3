from datetime import datetime, timedelta

from django.db.models import Count, Value
from django.db.models.functions import Concat
from django.http import HttpResponseNotFound
from django.db.models import F
from django.db.models.query import QuerySet
from django.utils.timezone import make_aware, utc
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from script_rules import update_pulled_pork
from .models import Event, Request, Rule
from .serializers import EventSerializer, EventCountAddressSerializer, EventCountRuleSerializer, RequestSerializer
from .serializers import RuleSerializer


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


class RequestList(generics.ListAPIView):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer

    def get_queryset(self) -> QuerySet:
        queryset = super().get_queryset()

        # checks if all params are included
        period_start = self.request.query_params.get('period_start')
        period_stop = self.request.query_params.get('period_stop')
        if not (period_start and period_stop):
            raise ValidationError({"error": "You should define 'period_start' and 'period_stop' in format DD-MM-YY"})

        # checks if params are proper"YYYY-MM-DD HH:MM:SS"
        try:
            period_start = datetime.strptime(period_start, "%Y-%m-%d %H:%M:%S")
            period_start = make_aware(period_start, utc)
            period_stop = datetime.strptime(period_stop, "%Y-%m-%d %H:%M:%S") + timedelta(days=1)
            period_stop = make_aware(period_stop, utc)

        except ValueError:
            # the format "YYYY-MM-DD" without time
            try:
                period_start = datetime.strptime(period_start, "%Y-%m-%d")
                period_start = make_aware(period_start, utc)
                period_stop = datetime.strptime(period_stop, "%Y-%m-%d") + timedelta(days=1)
                period_stop = make_aware(period_stop, utc)
            except ValueError:
                raise ValidationError({"error": "Use format YYYY-MM-DD HH:MM:SS or YYYY-MM-DD"})

        # checks if period is less than week
        if period_stop - period_start > timedelta(days=7):
            raise ValidationError({"error": "The range has to be less than a week"})

        queryset = queryset.filter(timestamp__gte=period_start, timestamp__lte=period_stop)
        return queryset


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

        # checking if type params are included
        if not type_of_filter:
            raise ValidationError({"error": "You should define 'type' of filter (sid or addr)"})

        # checking if period is known
        if period:
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


class RuleCreate(APIView):
    def post(self, request, *args, **kwargs) -> Response:
        """POST method, but uses script for checking changes in pulledpork3 rules"""
        count = update_pulled_pork('rules.txt')
        return Response({'message': f'{count} rules has been added'}, status=status.HTTP_201_CREATED)


def error404(request, exception):
    """
    default 404 response
    need DEBUG=False
    """
    return HttpResponseNotFound('{"error": "The request is malformed or invalid."}')


class RuleListView(generics.ListAPIView):
    queryset = Rule.objects.all()
    serializer_class = RuleSerializer

    def get_queryset(self):
        queryset = Rule.objects.all()

        sid = self.request.query_params.get('sid', None)
        rev = self.request.query_params.get('rev', None)
        action = self.request.query_params.get('action', None)

        if sid:
            queryset = queryset.filter(sid=sid)
        if rev:
            queryset = queryset.filter(rev=rev)
        if action:
            queryset = queryset.filter(action=action)

        return queryset

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

        except Exception:
            return Response({
                "error": "Bad Request", "message": "The request is malformed or invalid."},
                status=400)
