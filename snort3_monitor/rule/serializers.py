from rest_framework import serializers

from rule.models import Rule


class RuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rule
        fields = ('sid', 'rev', 'gid', 'action', 'message')
