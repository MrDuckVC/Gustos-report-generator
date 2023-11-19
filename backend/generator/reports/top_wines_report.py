from abc import abstractmethod

from django.http import HttpRequest

from generator.reports.report import Report


class TopWinesReport(Report):
    def __init__(self, request: HttpRequest):
        super().__init__(request)

        self.top_wine_url: str | None = None  # Url to the top wines on GWMR website.

    @abstractmethod
    def get_url(self) -> str:
        """
        Get the url to the top wines on GWMR website.

        :return: The url.
        """
        pass

    def render(self) -> str:
        """
        Render the report.

        :return: The rendered report.
        """
        self.top_wine_url = self.get_url()
        return self.render_template(
            "top_wines_report.html",
            **self.top_template_kwargs(),
        )

    def top_template_kwargs(self):
        """
        Get the template arguments for the top wines report.

        :return: The template arguments.
        """
        return {
            "top_wine_url": self.top_wine_url,
            "top_name": self.title,
        }
