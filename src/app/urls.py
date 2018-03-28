# -*- encoding: utf-8 -*-
from rest_framework import routers

from . import views

router = routers.DefaultRouter()  # DefaultRouter会生成rootview

router.register(r'services', views.ServiceViewSet)
router.register(r'tags', views.TagViewSet)
router.register(r'pings', views.PingViewSet)
