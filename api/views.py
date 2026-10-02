from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from api.serializers import (
    CourseSerializer,
    GroupSerializer,
    NewsSerializer,
    RoomSerializer,
    ShopItemSerializer,
)
from coins.models import ShopItem
from courses.models import Course, Group, Room
from news.models import News


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.all().order_by('title')
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.select_related('course', 'teacher__user', 'mentor').all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]


class RoomViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Room.objects.all().order_by('name')
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]


class NewsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NewsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return News.objects.filter(is_published=True).select_related('author')


class ShopItemViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ShopItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ShopItem.objects.filter(is_active=True, stock__gt=0)
