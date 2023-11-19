from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from generator.views import AjaxWineryView, IndexView, PersonalReportSectionView, SectionView, TasksView, TaskView

urlpatterns = [
    path("", IndexView.as_view(), name="home"),
    path("sections/personal_winery_report", csrf_exempt(PersonalReportSectionView.as_view()), name="personal_report"),
    path("sections/<section>", csrf_exempt(SectionView.as_view()), name="sections"),
    path("tasks", TasksView.as_view(), name="tasks"),
    path("tasks/<id>", TaskView.as_view(), name="task"),

    path("ajax/wineries", AjaxWineryView.as_view()),
]
