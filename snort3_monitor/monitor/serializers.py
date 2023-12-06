from rest_framework import serializers

from .models import Event, Rule



class RuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rule
        fields = ('sid', 'rev', 'action', 'message')


class EventSerializer(serializers.ModelSerializer):
    sid = serializers.SerializerMethodField()
    action = serializers.SerializerMethodField()
    message = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ('id', 'timestamp', 'sid', 'action', 'src_addr', 'src_port', 'dst_addr', 'dst_port', 'proto', 'message')

   
    def get_sid(self, obj: Event) -> str:
        return obj.rule.sid

    def get_action(self, obj: Event) -> str:
        return obj.rule.action

    def get_message(self, obj: Event) -> str:
        return obj.rule.message