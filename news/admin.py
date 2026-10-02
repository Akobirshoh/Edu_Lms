from django.contrib import admin

from .models import News


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "is_published", "created_at")
    list_filter = ("is_published",)
    search_fields = ("title", "body")

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)
