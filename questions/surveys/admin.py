from django.contrib import admin

from surveys.models import (
    Survey,
    SurveyQuestions,
    QuestionAnswerOption,
    SurveyCompleting,
    QuestionAnswer
)


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    """Администрирование опросов."""

    list_display = ("uid", "title", "created_at")
    list_editable = ("title",)
    search_fields = ("author__first_name", "author__last_name", "title")
    raw_id_fields = ("author",)
    show_full_result_count = False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("author")


@admin.register(SurveyQuestions)
class SurveyQuestionsAdmin(admin.ModelAdmin):
    """Администрирование списка вопросов."""

    list_display = ("survey__title", "text", "priority")
    list_editable = ("text", "priority")
    search_fields = ("survey__title", "text")
    show_full_result_count = False
    raw_id_fields = ("survey",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("survey")



@admin.register(QuestionAnswerOption)
class QuestionAnswerOptionAdmin(admin.ModelAdmin):
    """Администрирование списка вариантов ответов."""

    list_display = ("question", "text", "priority")
    list_editable = ("text", "priority")
    search_fields = ("question__text", "text")
    show_full_result_count = False
    raw_id_fields = ("question",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "question", "question__survey"
        )


@admin.register(SurveyCompleting)
class SurveyCompletingAdmin(admin.ModelAdmin):
    """Администрирование анкет прохождения опросов пользователями."""

    list_display = (
        "uid", "user__first_name", "user__last_name", "survey__title"
    )
    raw_id_fields = ("user", "survey")
    search_fields = ("user__firs_name", "user__last_name", "survey__title")
    show_full_result_count = False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user", "survey")


@admin.register(QuestionAnswer)
class QuestionAnswerAdmin(admin.ModelAdmin):
    """Администрирование списка ответов пользователей на вопросы."""

    list_display = ("form__uid", "form__survey__title", "question__text")
    raw_id_fields = ("question", "form", "answer_option")
    show_full_result_count = False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "form", "answer_option", "question", "form__survey"
        )
