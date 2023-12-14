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
from .serializers import EventSerializer, EventCountAddressSerializer, \
    EventCountRuleSerializer, RequestSerializer, RuleSerializer


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
            validate_params(params.keys(), allowed_params)

            # changing sid key
            if params.get('sid') is not None:
                params['rule__sid'] = params.pop('sid')

            if params.get('page') is not None:
                params.pop('page')

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

        allowed_params = ['period_start', 'period_stop']
        params = [key for key in self.request.query_params]
        validate_params(params, allowed_params)

        # checks if all params are included
        period_start = self.request.query_params.get('period_start')
        period_stop = self.request.query_params.get('period_stop')
        if not (period_start and period_stop):
            raise ValidationError({"error": "You should define 'period_start' and 'period_stop'."})

        # checks if format is proper
        period_start = self.validate_date(period_start)
        period_stop = self.validate_date(period_stop) + timedelta(days=1)

        # checks if period is less than week
        if period_stop - period_start > timedelta(days=7):
            raise ValidationError({"error": "The range has to be less than a week"})

        queryset = queryset.filter(timestamp__gte=period_start, timestamp__lte=period_stop)
        return queryset

    @staticmethod
    def validate_date(date):
        """Validating date format"""
        formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d %H", "%Y-%m-%d"]
        for frmt in formats:
            try:
                date = datetime.strptime(date, frmt)
                return make_aware(date, utc)
            except ValueError:
                pass
        raise ValidationError({"error": "Use format YYYY-MM-DD HH:MM:SS (you can skip SS, MM, HH)"})


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
                .order_by('count')
            )
        elif params.get('type') == 'sid':
            EventCountList.serializer_class = EventCountRuleSerializer
            queryset = (
                queryset
                .values(sid=F('rule__sid'))
                .annotate(count=Count('rule__sid'))
                .order_by('count')
            )
        else:
            raise ValidationError(
                {"error": "Unknown 'type', use 'sid' or 'addr'"})

        return queryset


class RuleCreate(APIView):
    def post(self, request, *args, **kwargs) -> Response:
        """POST method, but uses script for checking changes in pulledpork3 rules"""
        try:
            count = update_pulled_pork('rules.txt')
        except RuntimeError as e:
            return Response({'error': e}, status=status.HTTP_400_BAD_REQUEST)

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

        allowed_params = ['sid', 'rev', 'gid']
        params = [key for key in self.request.query_params]
        validate_params(params, allowed_params)
        sid = self.request.query_params.get('sid', None)
        rev = self.request.query_params.get('rev', None)
        gid = self.request.query_params.get('gid', None)
        if sid:
            queryset = queryset.filter(sid=sid)
        if rev:
            queryset = queryset.filter(rev=rev)
        if gid:
            queryset = queryset.filter(gid=gid)
        return queryset.order_by('sid', 'rev', 'gid')


def validate_params(entered, allowed: list) -> None:
    """
    validate query parameters
    """
    allowed.append('page')

    only_allowed_params_present = set(entered).issubset(set(allowed))
    if not only_allowed_params_present:
        raise ValidationError(
            {"error": f"You can use only {', '.join(allowed)} as query filters."})
