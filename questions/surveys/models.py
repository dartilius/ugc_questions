from uuid import uuid4

from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()

class Survey(models.Model):
    """Опрос."""

    uid = models.UUIDField(
        default=uuid4,
        verbose_name="Гуид",
        editable=False,
        primary_key=True
    )
    title = models.CharField(verbose_name="Название", max_length=255)
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        related_name="surveys",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(
        verbose_name="Дата создания",
        auto_now_add=True,
        editable=False
    )
    updated_at = models.DateTimeField(
        verbose_name="Дата последнего обновления",
        auto_now=True
    )

    def __str__(self):
        return f"{self.title} от {self.created_at}"

    class Meta:
        verbose_name = "Опрос"
        verbose_name_plural = "Опросы"
        # db_tabel = "surveys"
        ordering = ("-created_at",)


class SurveyQuestions(models.Model):
    """Вопрос опроса."""

    text = models.TextField(verbose_name="Текст вопроса")
    priority = models.SmallIntegerField(
        verbose_name="Приоритет вопроса в списке", default=0
    )
    survey = models.ForeignKey(
        Survey,
        verbose_name="Опрос",
        on_delete=models.CASCADE,
        related_name="questions"
    )

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"
        # db_tabel = "questions"
        ordering = ("-priority",)

    def __str__(self):
        return (
            f"{self.survey} - "
            f"{self.text[:50] + '...' if len(self.text) > 50 else self.text}"
        )

class QuestionAnswerOption(models.Model):
    """Вариант ответа."""

    text = models.TextField(verbose_name="Текст ответа")
    priority = models.IntegerField(
        verbose_name="Приоритет ответа в списке", default=0
    )
    question = models.ForeignKey(
        SurveyQuestions,
        verbose_name="Вопрос",
        on_delete=models.CASCADE,
        related_name="answer_options"
    )

    def __str__(self):
        return (
            f"{self.question} - "
            f"{self.text[:50] + '...' if len(self.text) > 50 else self.text}"
        )

    class Meta:
        verbose_name = "Вариант ответа"
        verbose_name_plural = "Варианты ответа"
        # db_tabel = "answer_options"
        ordering = ("-priority",)


class SurveyCompleting(models.Model):
    """Анкеты пользователя проходящего опрос."""

    uid = models.UUIDField(default=uuid4, verbose_name="Гуид", primary_key=True)
    start_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name="Дата начала прохождения опроса"
    )
    finish_at = models.DateTimeField(
        verbose_name="Дата завершения опроса", null=True, blank=True
    )
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь проходящий опрос",
        on_delete=models.SET_NULL,
        null=True,
        related_name="user_forms"
    )
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        verbose_name="Опрос",
        related_name="survey_forms"
    )

    def __str__(self):
        return (
            f"{self.user.last_name} {self.user.first_name} - "
            f"{self.survey}"
        )

    class Meta:
        verbose_name = "Анкета опроса"
        verbose_name_plural = "Анкеты опросов"
        # db_tabel = "survey_forms"


class QuestionAnswer(models.Model):
    """Ответ пользователя на вопрос."""

    question = models.ForeignKey(
        SurveyQuestions,
        on_delete=models.CASCADE,
        verbose_name="Вопрос",
        related_name="question_answers"
    )
    form = models.ForeignKey(
        SurveyCompleting,
        verbose_name="Анкета ответов пользователя",
        on_delete=models.CASCADE,
        related_name="form_answers"
    )
    answer_option = models.ForeignKey(
        QuestionAnswerOption,
        on_delete=models.CASCADE,
        verbose_name="Выбранный вариант ответа"
    )

    def __str__(self):
        return f"{self.form} {self.question}"

    class Meta:
        verbose_name = "Ответ на вопрос"
        verbose_name_plural = "Ответы на вопросы"
        # db_tabel = "answers"
