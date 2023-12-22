import logging
import threading

from django.db.models import QuerySet
from rest_framework import status, generics
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from rule.serializers import RuleSerializer
from rule.models import Rule
from script_rules import update_pulled_pork


logger = logging.getLogger('monitor')


class RuleCreate(APIView):
    @staticmethod
    def background_update():
        """Perform background updating of rules"""
        try:
            count = update_pulled_pork('rules.txt')
            logger.info(f"{count} new rules have been added.")
        except RuntimeError as e:
            logger.error(e)

    def post(self, request, *args, **kwargs) -> Response:
        """Start rules updating and send immediate response"""
        threading.Thread(target=self.background_update).start()
        return Response({'message': 'Update process started.'}, status=status.HTTP_202_ACCEPTED)


class RuleListView(generics.ListAPIView):
    queryset = Rule.objects.all()
    serializer_class = RuleSerializer

    def get_queryset(self) -> QuerySet:
        """Perform filtering and ordering data

        Client can use only allowed_params in query.
        """
        queryset = super().get_queryset()

        allowed_params = ['sid', 'rev', 'gid']
        params = [key for key in self.request.query_params]
        self.validate_params(params, allowed_params)

        sid = self.request.query_params.get('sid', None)
        rev = self.request.query_params.get('rev', None)
        gid = self.request.query_params.get('gid', None)
        if sid:
            queryset = queryset.filter(sid=sid)
        if rev:
            queryset = queryset.filter(rev=rev)
        if gid:
            queryset = queryset.filter(gid=gid)
        return queryset.order_by('sid', 'gid', 'rev')

    @staticmethod
    def validate_params(entered: list, allowed: list) -> None:
        """Validate query parameters

        :param entered: Params of query, which user entered
        :param allowed: Params that are allowed in endpoint
        """
        allowed.append('page')
        only_allowed_params_present = set(entered).issubset(set(allowed))
        if not only_allowed_params_present:
            raise ValidationError(
                {"error": f"You can use only {', '.join(allowed)} as query filters."})
