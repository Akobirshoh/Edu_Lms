from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    CourseViewSet,
    GroupViewSet,
    NewsViewSet,
    RoomViewSet,
    ShopItemViewSet,
)

router = DefaultRouter()
router.register('courses', CourseViewSet, basename='api-course')
router.register('groups', GroupViewSet, basename='api-group')
router.register('rooms', RoomViewSet, basename='api-room')
router.register('news', NewsViewSet, basename='api-news')
router.register('shop', ShopItemViewSet, basename='api-shop')

urlpatterns = [
    path('', include(router.urls)),
]
