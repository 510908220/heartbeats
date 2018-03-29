from django.shortcuts import render
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

# Create your views here.
import django_filters
from rest_framework import (authentication,
                            filters,
                            permissions,
                            viewsets)


from .models import Tag, Service, Ping
from .serializers import TagSerializer, ServiceSerializer, PingSerializer


class DefaultsMixin(object):
    authentication_classes = (
        authentication.BasicAuthentication,
        authentication.TokenAuthentication
    )
    permission_classes = (
        permissions.IsAuthenticated,
    )

    filter_backends = (
        django_filters.rest_framework.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    )


class M2MFilter(django_filters.Filter):

    def filter(self, qs, value):
        if not value:
            return qs

        values = value.split(',')
        for v in values:
            qs = qs.filter(tags=v)
        return qs


class ServiceFilter(django_filters.FilterSet):
    tags = M2MFilter(name='tags')

    class Meta:
        model = Service
        fields = ('tags',)


class TagViewSet(DefaultsMixin, viewsets.ModelViewSet):
    queryset = Tag.objects.order_by('created')
    serializer_class = TagSerializer
    ordering_fields = ('created', )

    def get_queryset(self):
        return self.queryset.all()


class PingViewSet(DefaultsMixin, viewsets.ModelViewSet):
    queryset = Ping.objects.order_by('created')
    serializer_class = PingSerializer
    filter_fields = ('service',)
    ordering_fields = ('created', )

    def get_queryset(self):
        return self.queryset.all()

    def create(self, request):
        short_url = request.query_params.get('service')
        service_obj = get_object_or_404(Service, short_url=short_url)

        headers = request.META
        remote_addr = headers.get("HTTP_X_FORWARDED_FOR", headers["REMOTE_ADDR"])
        remote_addr = remote_addr.split(",")[0]

        params = dict(self.request.data)
        params.update({
            'data': request.query_params.get('data'),
            'remote_addr': remote_addr,
            'ua': headers.get("HTTP_USER_AGENT", "")
        })
        ping = service_obj.pings.create(**params)

        return Response(PingSerializer(ping).data)


class ServiceViewSet(DefaultsMixin, viewsets.ModelViewSet):
    queryset = Service.objects.order_by('created')
    serializer_class = ServiceSerializer

    ordering_fields = ('updated', )
    filter_class = ServiceFilter
    filter_fields = ('tags', 'status', 'tp')

    def get_queryset(self):
        return self.queryset.all()

    def create(self, request):
        params = dict(self.request.data)
        tags = params.pop('tags', '')
        service = Service(**params)
        service.save()
        for tag in tags.strip().split(","):
            tag_obj, _ = Tag.objects.get_or_create(name=tag)
            service.tags.add(tag_obj)

        return Response(ServiceSerializer(service).data)

    def update(self, request, pk=None):
        params = dict(self.request.data)

        # 时间字段会自动更新的
        params.pop('created', '')
        params.pop('updated', '')

        # 取出tags字段, 先更新Service. 注意这里需要传入这样的格式['name1', 'name2']

        if 'tags' in params:
            tags = params.pop('tags')
            Service.objects.filter(pk=pk).update(**params)
            service = Service.objects.get(id=pk)
            service.tags.clear()
            for tag in tags.strip().split(","):
                tag_obj, _ = Tag.objects.get_or_create(name=tag)
                service.tags.add(tag_obj)
        else:
            Service.objects.filter(pk=pk).update(**params)
            service = Service.objects.get(id=pk)
        service.save()  # 更新时间字段
        return Response(ServiceSerializer(service).data)
