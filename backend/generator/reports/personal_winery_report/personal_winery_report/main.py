from generator.forms import WineryReportForm
from generator.reports.winery_report import WineryReport


class PersonalWineryReport(WineryReport):
    @property
    def title(self):
        return "Personal Winery Report"

    @property
    def weight(self):
        return 0

    def render(self):
        return ""

    def get_form(self, *args, **kwargs):
        self.form = WineryReportForm(*args, **kwargs)
        return self.form
