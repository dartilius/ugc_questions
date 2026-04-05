from django import forms
from django.forms import inlineformset_factory

from surveys.models import Survey, SurveyQuestions, QuestionAnswerOption


class SurveyForm(forms.ModelForm):
    """Форма опросов."""

    class Meta:
        model = Survey
        fields = ("title",)
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
        }


class SurveyQuestionForm(forms.ModelForm):
    class Meta:
        model = SurveyQuestions
        fields = ("text", "priority")
        widgets = {
            "text": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "priority": forms.NumberInput(attrs={"class": "form-control"}),
        }


class QuestionAnswerOptionForm(forms.ModelForm):
    class Meta:
        model = QuestionAnswerOption
        fields = ("text", "priority")
        widgets = {
            "text": forms.TextInput(attrs={"class": "form-control"}),
            "priority": forms.NumberInput(attrs={"class": "form-control"}),
        }


SurveyQuestionFormSet = inlineformset_factory(
    Survey,
    SurveyQuestions,
    form=SurveyQuestionForm,
    extra=3,
    can_delete=True,
    min_num=3,
    validate_min=True,
)

AnswerOptionFormSet = inlineformset_factory(
    SurveyQuestions,
    QuestionAnswerOption,
    form=QuestionAnswerOptionForm,
    extra=2,
    can_delete=True,
    min_num=2,
    validate_min=True,
)