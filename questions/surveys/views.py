from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Count, Q
from django.forms import inlineformset_factory, BaseInlineFormSet
from django.http import QueryDict, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods

from surveys.forms import SurveyForm, QuestionAnswerOptionForm, SurveyQuestionForm
from surveys.models import Survey, SurveyCompleting, SurveyQuestions, \
    QuestionAnswerOption, QuestionAnswer
from surveys.utils import get_page

LIMIT = 20


def index(request):
    template = 'surveys/index.html'
    surveys = Survey.objects.select_related("author").annotate(
        questions_count=Count("questions"),
        completing_count=Count(
            "survey_forms",
            filter=Q(survey_forms__finish_at__isnull=False)
        )
    )
    page_obj = get_page(request, surveys, LIMIT)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


class BaseSurveyQuestionFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        non_deleted_forms = [
            form for form in self.forms
            if not self._should_delete_form(form)
        ]
        if len(non_deleted_forms) < 3:
            raise ValidationError('Минимальное количество вопросов — 3.')


AnswerOptionFormSet = inlineformset_factory(
    SurveyQuestions,
    QuestionAnswerOption,
    form=QuestionAnswerOptionForm,
    extra=1,
    min_num=2,
    validate_min=True,
    can_delete=True,
)


SurveyQuestionFormSet = inlineformset_factory(
    Survey,
    SurveyQuestions,
    form=SurveyQuestionForm,
    formset=BaseSurveyQuestionFormSet,
    extra=0,
    min_num=3,
    validate_min=True,
    can_delete=True,
)


@login_required
@transaction.atomic
def create_survey(request):
    template="surveys/create.html"
    if request.method == "POST":
        form = SurveyForm(request.POST)
        question_formset = SurveyQuestionFormSet(request.POST)

        if form.is_valid() and question_formset.is_valid():
            survey = form.save(commit=False)
            survey.author = request.user
            survey.save()

            questions = question_formset.save(commit=False)
            for question in questions:
                question.survey = survey
                question.save()

                try:
                    form_index = [f.instance for f in question_formset.forms].index(question)
                except ValueError:
                    form_index = list(questions).index(question)

                prefix = f'questions-{form_index}-answers'
                total_forms_key = f'{prefix}-TOTAL_FORMS'
                initial_forms_key = f'{prefix}-INITIAL_FORMS'
                min_forms_key = f'{prefix}-MIN_NUM'
                max_forms_key = f'{prefix}-MAX_NUM'

                post_data = request.POST.copy()
                answer_keys = [k for k in post_data.keys() if k.startswith(f'{prefix}-') and '-text' in k]
                total_forms = len(answer_keys)

                post_data[total_forms_key] = str(total_forms)
                post_data[initial_forms_key] = '0'
                post_data[min_forms_key] = '2'
                post_data[max_forms_key] = str(total_forms)

                answer_formset = AnswerOptionFormSet(
                    post_data,
                    instance=question,
                    prefix=prefix
                )

                if answer_formset.is_valid():
                    answer_formset.save()
                else:
                    context = {
                        'form': form,
                        'question_formset': question_formset,
                    }
                    return render(request, 'surveys/create.html', context)

            return redirect('surveys:index')
    else:
        form = SurveyForm()
        question_formset = SurveyQuestionFormSet(queryset=SurveyQuestions.objects.none())

    context = {
        'form': form,
        'question_formset': question_formset,
        'is_edit': False,
    }
    return render(request, template, context)


@login_required
@transaction.atomic
def edit_survey(request, uid):
    survey = get_object_or_404(Survey.objects.prefetch_related(
        'questions__answer_options'
    ), uid=uid)

    if request.method == "POST":
        form = SurveyForm(request.POST, instance=survey)
        question_formset = SurveyQuestionFormSet(request.POST, instance=survey)

        if form.is_valid() and question_formset.is_valid():
            survey = form.save()
            questions = question_formset.save(commit=False)
            for question in questions:
                question.survey = survey
                question.save()
                answer_formset = AnswerOptionFormSet(
                    request.POST,
                    instance=question,
                    prefix=f'answers-{question.id}'
                )
                if answer_formset.is_valid():
                    answer_formset.save()
                else:
                    messages.error(request, f"Ошибка в вариантах ответа для вопроса: {question.text}")
                    return render(request, "surveys/edit.html", {
                        "form": form,
                        "question_formset": question_formset,
                        "is_edit": True,
                        "survey": survey,
                    })

            question_formset.save_m2m()
            messages.success(request, "Опрос успешно обновлён!")
            return redirect("surveys:index")
    else:
        form = SurveyForm(instance=survey)
        question_formset = SurveyQuestionFormSet(instance=survey)
        for question_form in question_formset.forms:
            if question_form.instance.pk:
                question_form.answers = AnswerOptionFormSet(
                    instance=question_form.instance,
                    prefix=f'answers-{question_form.instance.id}'
                )
            else:
                question_form.answers = AnswerOptionFormSet(
                    instance=question_form.instance,
                    prefix='answers-new'
                )

    return render(request, "surveys/edit.html", {
        "form": form,
        "question_formset": question_formset,
        "is_edit": True,
        "survey": survey,
    })


@login_required
def start_survey_completing(request, uid):
    template = "surveys/completing.html"
    survey = get_object_or_404(
        Survey.objects.prefetch_related(
            "questions", "questions__answer_options"
        ),
        uid=uid
    )
    completing, _ = SurveyCompleting.objects.get_or_create(
        user=request.user,
        survey=survey
    )
    return render(request, template, {'survey': survey})


@login_required
def complete_survey(request, uid):
    """Завершает прохождение опроса."""
    survey = get_object_or_404(
        Survey.objects.prefetch_related("questions"), uid=uid
    )
    user= request.user
    form = get_object_or_404(
        SurveyCompleting.objects.prefetch_related(
            "form_answers"
        ), survey=survey, user=user
    )
    if form.form_answers.count() != survey.questions.count():
        messages.error(
            request,
            "Невозможно завершить опрос, вы ответили не на все вопросы!"
        )
    else:
        form.finish_at = datetime.now()
        form.save(update_fields=["finish_at"])
        return redirect("surveys:index")


@login_required
@require_http_methods(["POST"])
def add_answer(request, uid, q_id):
    """Сохраняет ответ на вопрос опроса."""
    survey = get_object_or_404(Survey, uid=uid)
    user = request.user
    form = get_object_or_404(SurveyCompleting, user=user, survey=survey)

    if form.finish_at is not None:
        return JsonResponse({"error": "Вы уже завершили опрос."}, status=400)

    answer_option_id = request.POST.get("answer_option")
    if not answer_option_id:
        return JsonResponse({"error": "Не выбран вариант ответа."}, status=400)

    try:
        answer_option = get_object_or_404(QuestionAnswerOption, id=answer_option_id)
        QuestionAnswer.objects.update_or_create(
            question_id=q_id,
            form=form,
            defaults={"answer_option": answer_option}
        )
        return JsonResponse({"success": "Ответ сохранён."})
    except Exception as e:
        return JsonResponse({"error": "Ошибка при сохранении ответа."}, status=500)