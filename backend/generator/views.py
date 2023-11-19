from io import BytesIO

from django.contrib import messages
from django.core.paginator import Paginator
from django.http import FileResponse, HttpRequest, HttpResponseNotFound, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django.views import View
from sqlalchemy import func, select

from generator.exceptions import DataNotFoundException, RatingNotFoundException
from generator.forms import SectionForm
from generator.models import Task, TaskLogEntry
from generator.reports.personal_winery_report.personal_winery_report.main import PersonalWineryReport
from generator.utils.database import Database
from generator.utils.report import generating_pdf_report, get_report, get_section, SubsectionsBySections
from gustos.models import winery

PAGE_SIZE = 20


class IndexView(View):
    def get(self, request):
        return render(request, "generator/pages/index.html", {
            "title": _("Home"),
        })


class SectionView(View):
    def get(self, request: HttpRequest, section):
        SubsectionsBySections.get_subsections_by_sections()

        if section not in SubsectionsBySections.subsections_by_sections:
            return HttpResponseNotFound()

        section_info = get_section(section)

        subsections = {subsection: get_report(request, section, subsection) for subsection in SubsectionsBySections.subsections_by_sections[section]}
        subsections = ((subsection, report.title) for subsection, report in sorted(subsections.items(), key=lambda subsection: subsection[1].weight))

        form = SectionForm(subsections=subsections)

        return render(request, "generator/pages/subsection.html", {
            "title": section_info.name,
            "form": form,
        })

    def post(self, request: HttpRequest, section):
        SubsectionsBySections.get_subsections_by_sections()
        SubsectionsBySections.get_sections_by_chapters()

        if section not in SubsectionsBySections.subsections_by_sections:
            return HttpResponseNotFound()

        section_info = get_section(section)

        preview = ""
        subsections = {subsection: get_report(request, section, subsection) for subsection in SubsectionsBySections.subsections_by_sections[section]}
        subsections = tuple((subsection, report.title) for subsection, report in sorted(subsections.items(), key=lambda subsection: subsection[1].weight))

        form = SectionForm(request.POST, subsections=subsections)

        if form.is_valid():
            subsection = form.cleaned_data.get("subsection")
            report = get_report(request, section, subsection)

            try:
                # Check if POST request is triggered by "Preview" button of report form.
                if request.POST.get("op") == "preview":
                    form = report.get_form(request.POST, subsections=subsections)
                    if form.is_valid():
                        preview = report.render()
                # Check if POST request is triggered by "Generate" button of report form.
                elif request.POST.get("op") == "generate":
                    form = report.get_form(request.POST, subsections=subsections)
                    if form.is_valid():
                        preview = report.render()
                        output = BytesIO()
                        generating_pdf_report(preview, output)
                        output.seek(0)
                        return FileResponse(output, filename=f"{subsection}_{form.cleaned_data.get('winery')}_{form.cleaned_data.get('year_from')}_{form.cleaned_data.get('year_to')}.pdf")
                # Means that POST request is triggered by "Next" button.
                else:
                    form = report.get_form(initial=form.cleaned_data, subsections=subsections)
            except RatingNotFoundException:
                messages.error(request, _("Missing GWMR ratings for selected period. It seems that GWMR for selected period must be calculated in Gustos application first."))
            except DataNotFoundException:
                messages.error(request, _("Winery is missing in result data. It seems that winery does not have awarded wines which satisfy the criteria."))
        return render(
            request, "generator/pages/subsection.html", {
                "title": section_info.name,
                "form": form,
                "preview": preview
            }
        )


class PersonalReportSectionView(View):
    def get(self, request: HttpRequest):
        report = PersonalWineryReport(request)

        return render(
            request, "generator/pages/subsection.html", {
                "title": report.title,
                "form": report.get_form(),
            }
        )

    def post(self, request: HttpRequest):
        report = PersonalWineryReport(request)

        form = report.get_form(request.POST)

        if form.is_valid():
            task = report.enqueue_report_generation()
            messages.success(request, mark_safe(_("Task \"%(id)s\" has been created successfully.") % { "id": f'<a href="{reverse("task", args=[task.id])}">{task.id}</a>' }))

        return render(
            request, "generator/pages/subsection.html", {
                "title": report.title,
                "form": form,
            }
        )



class TasksView(View):
    def get(self, request: HttpRequest):
        tasks = Task.objects.all()
        paginator = Paginator(tasks, 15)
        page = request.GET.get("page")
        tasks = paginator.get_page(page)

        return render(request, "generator/pages/tasks.html", {
            "title": _("Tasks"),
            "tasks": tasks,
        })


class TaskView(View):
    def get(self, request: HttpRequest, id: str):
        try:
            task = Task.objects.get(id=id)
        except Task.DoesNotExist:
            return HttpResponseNotFound()

        log_entries = TaskLogEntry.objects.filter(task_id=task.id)
        paginator = Paginator(log_entries, 15)
        page = request.GET.get("page")
        log_entries = paginator.get_page(page)

        return render(
            request, "generator/pages/task.html", {
                "title": _('Task "%(id)s"') % { "id": task.id },
                "task": task,
                "log_entries": log_entries,
                # TODO: Make template tag for progress bar.
                # TODO: Mark progress bar with colors depending on slide errors.
                "progress": round(task.current / task.total * 100),
            }
        )


class AjaxWineryView(View):
    def get(self, request):
        term = request.GET.get("term")
        page = int(request.GET.get("page") or "1")
        offset = (page - 1) * PAGE_SIZE

        with Database().connect() as connection:
            subquery = select(func.count()).select_from(winery).order_by("id")
            if term:
                subquery = subquery.where(winery.c.name.like(f"%{term}%"))

            query = select(func.ifnull(subquery, 0))
            result = connection.execute(query)
            total, = result.fetchone()

            query = select(winery.c.id, winery.c.name).order_by(winery.c.id).limit(PAGE_SIZE).offset(offset)
            if term:
                query = query.where(winery.c.name.like(f"%{term}%"))
            result = connection.execute(query)
            results = result.fetchall()

        return JsonResponse({
            "results": [{"id": v[0], "text": v[1]} for v in results],
            "pagination": {
                "more": offset + len(results) < total
            },
        })
