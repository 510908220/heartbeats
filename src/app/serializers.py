from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework.exceptions import ValidationError
from .models import Tag, Service, Ping

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'created', 'updated')


class PingSerializer(serializers.ModelSerializer):
    service = serializers.SlugRelatedField(
        slug_field='name',
        required=False,
        allow_null=True,
        queryset=Service.objects.all()
    )

    class Meta:
        model = Ping
        fields = ('id', 'service', 'remote_addr', 'ua', 'data', 'created')


class ServiceSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    last_ping = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = ('id', 'name', 'status', 'tp',
                  'value', 'grace', 'short_url',
                  'tags', 'last_ping', 'notify_to',
                  'created', 'updated')

    def get_last_ping(self, obj):
        latest_pings = obj.pings.order_by('-id')[:1]
        if not latest_pings:
            return {}
        latest_ping = latest_pings[0]
        return PingSerializer(latest_ping).data
