from datetime import datetime
from typing import Mapping

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from generator.enum import Continent
from gustos.models import Winery, TaxonomyTerm
from main.settings import Database


class ReportForm(forms.Form):
    year_from = forms.ChoiceField(choices=((year, year) for year in range(datetime.now().year, 2019, -1)))
    year_to = forms.ChoiceField(choices=((year, year) for year in range(datetime.now().year, 2019, -1)))

    def clean_year_from(self):
        year_from = self.cleaned_data.get("year_from")
        year_to = self.data.get("year_to")

        errors = list()

        if year_to and year_to and year_to < year_from:
            errors.append(_("Start of the period cannot be greater than end of one."))

        if len(errors) > 0:
            raise ValidationError(errors)
        return year_from


class SectionForm(forms.Form):
    template_name = "generator/forms/section.html"

    subsection = forms.ChoiceField(label=_("Subsection"), choices=())

    def __init__(self, *args, **kwargs):
        subsections = kwargs.pop("subsections")

        super().__init__(*args, **kwargs)

        self.fields["subsection"].choices = subsections


class DefaultReportForm(SectionForm, ReportForm):
    template_name = "generator/forms/default_report.html"


class WineryReportForm(ReportForm):
    template_name = "generator/forms/winery_report.html"

    winery = forms.ChoiceField(choices=())
    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        if isinstance(data, Mapping):
            winery_id = data.get("winery")
            if winery_id is not None:
                self.fields["winery"].choices = tuple(Winery.objects.using(Database.GUSTOS.value).values_list("id", "name").filter(id=winery_id))


class CoefficientReportForm(SectionForm, ReportForm):
    template_name = "generator/forms/coefficients_report.html"

    coefficient = forms.FloatField(label=_("Coefficients"), initial=1.0)


class ContinentReportForm(SectionForm, ReportForm):
    template_name = "generator/forms/continent_report.html"

    continent = forms.ChoiceField(choices=((continent.value, continent.name.replace("_", " ")) for continent in Continent))


class CountryReportForm(SectionForm, ReportForm):
    template_name = "generator/forms/country_report.html"

    country = forms.ChoiceField(choices=(tuple(TaxonomyTerm.objects.using(Database.GUSTOS.value).values_list("tid", "name").filter(vid=3))))


class SectionWineryReportForm(WineryReportForm, SectionForm):
    template_name = "generator/forms/section_winery_report.html"
