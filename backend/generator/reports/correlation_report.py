import base64
from abc import abstractmethod
from io import BytesIO
from typing import List, Tuple

from django.http import HttpRequest
from matplotlib import pyplot as plt
from sqlalchemy import Select, select, func

from generator.reports.report import Report
from generator.utils.database import apply_range_filter

from gustos.models import (
    competition,
    event, award, award_wine_entity, wine_gwmr,
)


class CorrelationReport(Report):
    def __init__(self, request: HttpRequest):
        super().__init__(request)

        self.image_base64: str | None = None  # Base64 encoded image with correlation diagram.

    @property
    @abstractmethod
    def x_column_name(self) -> str:
        """
        :return: Name of column with x value.
        """
        pass

    @property
    @abstractmethod
    def y_column_name(self) -> str:
        """
        :return: Name of column with y value.
        """
        pass

    def build_query_for_correlation_between_gwmr_and_competition_rating(
            self,
            countries_ids: List[int] | Tuple[int] | int | None = None,
            event_year: Tuple[int, int] = None,
    ) -> Select:
        """
        Build query for correlation between GWMR and competition rating by countries of wine entity.

        :param event_year: Range of years of competition.
        :param countries_ids: Collection of countries ids or single country id.

        :return: SQLAlchemy query object.
        """

        we_subquery = self.build_query_for_wine_entity(
            countries=countries_ids,
            event_year=event_year,
        ).alias("we_subquery")

        return apply_range_filter(
            apply_range_filter(
                select(
                    func.sum(competition.c.rating).label(self.x_column_name),
                    wine_gwmr.c.rating.label(self.y_column_name),
                ).select_from(award_wine_entity) \
                    .join(award, award_wine_entity.c.award_id == award.c.id) \
                    .join(event, award.c.event_id == event.c.id) \
                    .join(competition, event.c.competition_id == competition.c.id) \
                    .join(we_subquery, award_wine_entity.c.wine_entity_id == we_subquery.c.id) \
                    .join(wine_gwmr, wine_gwmr.c.wine_entity_id == we_subquery.c.id) \
                    .where(
                        wine_gwmr.c.rating.is_not(None),
                    wine_gwmr.c.rating >= 60,
                    ) \
                    .group_by(award_wine_entity.c.wine_entity_id),
                (wine_gwmr.c.year_from, wine_gwmr.c.year_to),
                event_year
            ),
            event.c.year,
            event_year
        )

    def build_query_for_correlation_between_gwmr_and_medal_count(
            self,
            countries_ids: List[int] | Tuple[int] | int | None = None,
            event_year: Tuple[int, int] = None,
    ) -> Select:
        """
        Build query for correlation between GWMR and medal count by countries of wine entity.

        :param event_year: Range of years of competition.
        :param countries_ids: Collection of countries ids or single country id.

        :return: SQLAlchemy query object.
        """
        we_subquery = self.build_query_for_wine_entity(
            countries=countries_ids,
            event_year=event_year,
        ).alias("we_subquery")

        a_subquery = apply_range_filter(
            select(
                award
            ).select_from(award) \
                .join(event, award.c.event_id == event.c.id) \
                .where(award.c.id == award_wine_entity.c.award_id),
            event.c.year,
            event_year
        )

        return apply_range_filter(
            select(
                func.count(award_wine_entity.c.award_id).label(self.x_column_name),
                wine_gwmr.c.rating.label(self.y_column_name),
            ).select_from(award_wine_entity) \
                .join(we_subquery, award_wine_entity.c.wine_entity_id == we_subquery.c.id) \
                .join(wine_gwmr, wine_gwmr.c.wine_entity_id == we_subquery.c.id) \
                .where(
                    wine_gwmr.c.rating.is_not(None),
                wine_gwmr.c.rating >= 60,
                    a_subquery.exists()
                ) \
                .group_by(award_wine_entity.c.wine_entity_id),
            (wine_gwmr.c.year_from, wine_gwmr.c.year_to),
            event_year
        )

    @abstractmethod
    def get_query(self) -> Select:
        """
        :return: SQLAlchemy query object.
        """
        pass

    def render(self):
        query = self.get_query()

        with self.database.connect() as connection:
            # TODO: make more beautiful diagram and may be optimize code.
            # https://www.data-to-viz.com/graph/density2d.html
            # https://www.kyle-w-brown.com/R-Gallery/correlation.html

            result = connection.execute(query).mappings().fetchall()
            x = []
            y = []
            for row in result:
                x.append(float(row[self.x_column_name]))
                y.append(float(row[self.y_column_name]))

            # Calculate the trend line.
            n = len(x)
            if n == 0:
                return self.render_template(
                    "problem.html",
                    problem_message="No data for correlation."
                )

            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum([x[i] * y[i] for i in range(n)])
            sum_x_squared = sum([x[i] ** 2 for i in range(n)])

            # line equation: y = slope * x + y_intercept
            # slop - tangent of angle between line and x-axis
            # y_intercept - line intersection with y-axis
            if sum_x_squared - sum_x != 0:
                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x_squared - sum_x ** 2)
                y_intercept = (sum_y - slope * sum_x) / n

                # Plot trend line.
                plt.plot(x, [slope * i + y_intercept for i in x], '-', color="r")
            else:
                # If all x values are the same, plot a vertical line. This is a special case, because the slope is infinite.
                plt.axvline(x=sum_x / n, color="r")

            # Plot the data.
            plt.plot(x, y, ".", color="b")

            # Set the axes labels.
            plt.ylim(60, 100)

            # Add labels to the plot.
            plt.xlabel(self.x_column_name)
            plt.ylabel(self.y_column_name)

            # Save plot to stream.
            buffer = BytesIO()
            plt.savefig(buffer, format="png")
            self.image_base64 = f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode('utf-8')}"
            plt.close()

        return self.render_template(
            "correlation_report.html",
            **self.to_template_kwargs()
        )

    def to_template_kwargs(self) -> dict:
        """
        :return: Dictionary which will be passed as keyword arguments to the render_template function.
        """

        return {
            "image_base64": self.image_base64,
        }

