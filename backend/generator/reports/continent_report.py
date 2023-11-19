from abc import ABC

from django.http import HttpRequest

from generator.forms import ContinentReportForm
from generator.reports.report import Report


class ContinentReport(Report, ABC):
    def __init__(self, request: HttpRequest):
        super().__init__(request)

    def get_form(self, *args, **kwargs):
        self.form = ContinentReportForm(*args, **kwargs)
        return self.form

    @property
    def continent(self):
        if self.form is not None:
            continent = self.form.cleaned_data.get("continent")
        else:
            continent = self.request.POST.get("continent") or self.request.GET.get("continent")
        if continent is not None:
            return int(continent)
        return None
