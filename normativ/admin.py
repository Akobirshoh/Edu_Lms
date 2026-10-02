from django.contrib import admin

from .models import Normativ, NormativAnswer, NormativQuestion


class NormativQuestionInline(admin.TabularInline):
    model = NormativQuestion
    extra = 0


@admin.register(Normativ)
class NormativAdmin(admin.ModelAdmin):
    list_display = ("title", "lesson")
    search_fields = ("title",)
    inlines = [NormativQuestionInline]


@admin.register(NormativQuestion)
class NormativQuestionAdmin(admin.ModelAdmin):
    list_display = ("normativ", "order", "max_score")


@admin.register(NormativAnswer)
class NormativAnswerAdmin(admin.ModelAdmin):
    list_display = ("student", "question", "score", "checked_at")
    list_filter = ("score",)
    readonly_fields = ("created_at", "updated_at")
