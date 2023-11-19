from abc import ABC

from django.http import HttpRequest

from generator.forms import CountryReportForm
from generator.reports.report import Report


class CountryReport(Report, ABC):
    def __init__(self, request: HttpRequest):
        super().__init__(request)

    def get_form(self, *args, **kwargs):
        self.form = CountryReportForm(*args, **kwargs)
        return self.form

    @property
    def country(self):
        if self.form is not None:
            country = self.form.cleaned_data.get("country")
        else:
            country = self.request.POST.get("country") or self.request.GET.get("country")
        if country is not None:
            return int(country)
        return None
