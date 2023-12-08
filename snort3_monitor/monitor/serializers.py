from rest_framework import serializers

from .models import Event, Rule, Request


class RuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rule
        fields = ('sid', 'rev', 'gid', 'action', 'message')


class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):
    sid = serializers.SerializerMethodField()
    action = serializers.SerializerMethodField()
    message = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ('id', 'timestamp', 'sid', 'action', 'src_addr',
                  'src_port', 'dst_addr', 'dst_port', 'proto', 'message')

    @staticmethod
    def get_sid(obj):
        return obj.rule.sid

    @staticmethod
    def get_action(obj):
        return obj.rule.action

    @staticmethod
    def get_message(obj):
        return obj.rule.message


class EventCountAddressSerializer(serializers.Serializer):
    addr_pair = serializers.CharField(max_length=128)
    count = serializers.IntegerField()


class EventCountRuleSerializer(serializers.Serializer):
    sid = serializers.CharField(max_length=128)
    count = serializers.IntegerField()
