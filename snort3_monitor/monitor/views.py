from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from .models import Event
from .serializers import EventSerializer 



class EventListUpdate(generics.UpdateAPIView, generics.ListAPIView):
    queryset = Event.objects.filter(mark_as_deleted=False)
    serializer_class = EventSerializer

    def get_queryset(self):
        allowed_params = ['src_addr', 'src_port', 'dst_addr', 'dst_port', 'sid', 'proto']
        queryset = super().get_queryset()

        if self.request.method == 'PATCH':
            return queryset

        params = self.request.query_params
        params = {key: value for key, value in params.items()}
        if params:
            only_allowed_params_present = set(params.keys()).issubset(set(allowed_params))
            if not only_allowed_params_present:
                raise ValidationError(
                    {"error": "You can use only 'src_addr', 'src_port', 'dst_addr', 'dst_port', "
                              "'sid' and 'proto' to filter events"})
            if params.get('sid'):
                params['rule__sid'] = params.pop('sid')

            queryset = queryset.filter(**params)
        return queryset

    def patch(self, request, *args, **kwargs)-> Response:
        queryset = self.get_queryset()
        queryset.update(mark_as_deleted=True)
        return Response({"message": "All events are marked as deleted."})
