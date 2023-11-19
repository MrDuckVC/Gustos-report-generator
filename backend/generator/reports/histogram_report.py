import base64
from abc import abstractmethod
from io import BytesIO
from typing import Dict, Any, Tuple, List

import matplotlib.pyplot as plt
import seaborn as sns
from django.http import HttpRequest
from sqlalchemy import Select, func

from generator.reports.report import Report
from generator.utils.database import apply_range_filter
from gustos.models import wine_gwmr, wine_entity


class HistogramReport(Report):
    def __init__(self, request: HttpRequest):
        super().__init__(request)

        self.histograms: List[Dict[str, str]] = []  # Dictionary of histograms base64 encoded images by arguments.

    @property
    @abstractmethod
    def get_query_args(self) -> Dict[Any, str]:
        """
        Arguments to be passed to get_query() method.

        :return: Dictionary of arguments where key is argument value and value is argument name.
        """
        pass

    @abstractmethod
    def get_query(self, argument) -> Select:
        pass

    def build_query_by_wine_entity(
            self,
            countries: Tuple[int, ...] | int = None,
            we=wine_entity.alias("we"),
    ):
        wg = wine_gwmr.alias("wg")

        return apply_range_filter(
            self.build_query_for_wine_entity(
                select_fields=(
                    func.round(wg.c.rating, 2),
                    func.count(we.c.id),
                ),
                countries=countries,
                we=we,
                wg=wg,
            ) \
                .join(wg, wg.c.wine_entity_id == we.c.id),
            (wg.c.year_from, wg.c.year_to),
            (self.year_from, self.year_to),
        ).group_by(func.round(wg.c.rating, 2))

    def render(self) -> str:
        for argument, name in self.get_query_args.items():
            print(name)
            query = self.get_query(argument)

            with self.database.connect() as connection:
                result = connection.execute(query)
                gwmrs = []
                counts = []

                for gwmr, count in result:
                    gwmrs.append(gwmr)
                    counts.append(count)

            try:
                histogram_plot = sns.histplot(x=gwmrs, weights=counts, kde=True, bins=10)
                plt.xlim(60, 100)
                plt.xlabel("GWMR Rating")
            except ValueError:
                continue
            fig = histogram_plot.get_figure()

            buffer = BytesIO()
            fig.savefig(buffer, format="png")

            info = {
                "image_base64": f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode('utf-8')}",
                "name": name,
            }
            self.histograms.append(info)
            fig.clf()

        return self.render_template(
            template_name="histogram_report.html",
            **self.to_template_kwargs(),
        )

    def to_template_kwargs(self) -> dict:
        """
        Convert report data to a dictionary of values to be passed to the template.

        :return: Dictionary of values to be passed to the template.
        """
        return {
            "histograms": self.histograms,
        }
