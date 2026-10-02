from rest_framework import serializers

from coins.models import ShopItem
from courses.models import Course, Group, Room
from news.models import News


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'duration_months', 'is_active', 'created_at']


class GroupSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    teacher_name = serializers.CharField(source='teacher.user.get_full_name', read_only=True)

    class Meta:
        model = Group
        fields = [
            'id',
            'name',
            'course',
            'course_title',
            'teacher',
            'teacher_name',
            'mentor',
            'start_date',
            'is_active',
            'created_at',
        ]


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'name', 'capacity', 'created_at']


class NewsSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)

    class Meta:
        model = News
        fields = [
            'id',
            'title',
            'body',
            'image',
            'author',
            'author_name',
            'is_published',
            'created_at',
        ]


class ShopItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopItem
        fields = ['id', 'name', 'image', 'price', 'stock', 'is_active', 'created_at']
