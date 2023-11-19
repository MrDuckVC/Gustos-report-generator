from abc import ABC

from django.forms import Form
from django.http import HttpRequest

from generator.forms import CoefficientReportForm
from generator.reports.report import Report



class CoefficientReport(Report, ABC):
    """
    Report for coefficients.
    """
    def __init__(self, request: HttpRequest):
        super().__init__(request)

    def get_form(self, *args, **kwargs) -> Form:
        self.form = CoefficientReportForm(*args, **kwargs)
        return self.form

    @property
    def coefficient(self):
        if self.form is not None:
            coefficient = self.form.cleaned_data.get("coefficient")
        else:
            coefficient = self.request.POST.get("coefficient") or self.request.GET.get("coefficient")
        if coefficient is not None:
            return float(coefficient)
        return None
