from datetime import timedelta, datetime

from django.db.models import QuerySet
from django.utils.timezone import make_aware, utc
from rest_framework import generics
from rest_framework.exceptions import ValidationError

from request_log.models import Request
from request_log.serializers import RequestSerializer


class RequestList(generics.ListAPIView):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer

    def get_queryset(self) -> QuerySet:
        """Perform filtering and ordering data

        Client can use only allowed_params in query.
        """
        queryset = super().get_queryset()

        allowed_params = ['period_start', 'period_stop']
        params = [key for key in self.request.query_params]
        self.validate_params(params, allowed_params)

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
        return queryset.order_by('id')

    @staticmethod
    def validate_date(date: str) -> datetime:
        """Validate date format

        Only formats(list) are allowed in query.
        """
        formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d %H", "%Y-%m-%d"]
        for frmt in formats:
            try:
                date = datetime.strptime(date, frmt)
                return make_aware(date, utc)
            except ValueError:
                pass
        raise ValidationError({"error": "Use format YYYY-MM-DD HH:MM:SS (you can skip SS, MM, HH)"})

    @staticmethod
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
