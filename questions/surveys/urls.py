from django.urls import path
from . import views

app_name = 'surveys'

urlpatterns = [
    path("", views.index, name="index"),
    path("create", views.create_survey, name="create_survey"),
    path(
        "start_completing/<str:uid>",
        views.start_survey_completing,
        name="start_completing"
    ),
    path("survey/<str:uid>/complete", views.complete_survey, name="complete"),
    path("survey/<str:uid>/question/<int:q_id>/answer", views.add_answer,
         name='add_answer'),
    path("survey/<str:uid>/edit", views.edit_survey, name="edit")
]