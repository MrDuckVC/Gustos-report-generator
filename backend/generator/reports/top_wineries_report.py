from abc import abstractmethod
from typing import List, Tuple, Sequence

from django.http import HttpRequest
from sqlalchemy import Select, select, func, case

from generator.reports.report import Report
from generator.enum import WineType, WineColor, GrapeVariety
from generator.utils.database import apply_range_filter

from gustos.models import (
    winery, award_wine_entity,
    taxonomy_term, wine_entity,
    file_managed, wine,
    event, award,
)


class TopWineriesReport(Report):
    def __init__(self, request: HttpRequest):
        super().__init__(request)

        self.top_wineries: List[dict] = []
        """List of top wineries. Each dict contains information about winery, where keys are parameters names and values are values of parameters."""
        """Required keys: image (link to winery logo), name (winery name), country (country name), value (value of parameter), value_name (name of parameter)."""

    @property
    def image_column_name(self) -> str:
        """
        :return: Name of column with image.
        """
        return "image"

    @property
    def winery_column_name(self) -> str:
        """
        :return: Name of column with name.
        """
        return "name"

    @property
    def country_column_name(self) -> str:
        """
        :return: Name of column with country.
        """
        return "country"

    @property
    def value_column_name(self) -> str:
        """
        :return: Name of column with value.
        """
        return "value"

    @property
    @abstractmethod
    def value_name(self) -> str:
        """
        :return: Name of main parameter.
        """
        return "value_name"

    @abstractmethod
    def get_query(self) -> Select:
        """
        :return: SQLAlchemy query object.
        """
        pass

    def build_query_for_top_wineries_by_medal_count(
            self,
            countries_ids: List[int] | Tuple[int] | int | None = None,
            wine_color: Tuple[WineColor, ...] | WineColor = None,
            wine_type: Tuple[WineType, ...] | WineType = None,
            grape_variety: GrapeVariety = None,
            event_year: Tuple[int, int] = None,
    ) -> Select:
        """
        Build query for top wineries by medal count.
        :param event_year: Event year.
        :param countries_ids: Collection of countries ids or single country id.
        :param wine_color: Wine color.
        :param wine_type: Wine type.
        :param grape_variety: Grape variety.

        :return: SQLAlchemy query object.
        """
        we_subquery = self.build_query_for_wine_entity(
            wine_color=wine_color,
            wine_type=wine_type,
            grape_variety=grape_variety,
            event_year=event_year,
            we=wine_entity,
        ).alias("we_subquery")

        subquery = apply_range_filter(
            select(
                winery.c.name.label(self.winery_column_name),
                taxonomy_term.c.name.label(self.country_column_name),
                func.count(award_wine_entity.c.award_id).label(self.value_column_name),
                case(
                    (file_managed.c.uri.like("public://%"), func.concat("https://gustos.local/files/", func.substr(file_managed.c.uri, len("public://") + 1))),
                ).label(self.image_column_name),
                func.rank().over(order_by=func.count(award_wine_entity.c.award_id).desc()).label("position"),
            ).select_from(award_wine_entity) \
                .join(award, award.c.id == award_wine_entity.c.award_id) \
                .join(event, event.c.id == award.c.event_id) \
                .join(we_subquery, we_subquery.c.id == award_wine_entity.c.wine_entity_id) \
                .join(wine, wine.c.id == we_subquery.c.wine) \
                .join(winery, winery.c.id == wine.c.winery) \
                .join(taxonomy_term, taxonomy_term.c.tid == winery.c.country) \
                .outerjoin(file_managed, file_managed.c.fid == winery.c.logo) \
                .group_by(winery.c.id),
            event.c.year,
            event_year,
        )

        if countries_ids is not None:
            if not isinstance(countries_ids, Sequence):
                countries_ids = (countries_ids,)

            subquery = subquery.where(winery.c.country.in_(countries_ids))

        return select(
            getattr(subquery.c, self.winery_column_name),
            getattr(subquery.c, self.image_column_name),
            getattr(subquery.c, self.country_column_name),
            getattr(subquery.c, self.value_column_name),
        ).select_from(subquery) \
            .where(subquery.c.position <= 8) \
            .order_by(subquery.c.position)

    def render(self):
        query = self.get_query()

        with self.database.connect() as connection:
            result = connection.execute(query).mappings()
            for row in result:
                self.top_wineries.append({
                    "image": row[self.image_column_name] if row[self.image_column_name] else None,
                    "name": row[self.winery_column_name],
                    "country": row[self.country_column_name],
                    "value": row[self.value_column_name],
                    "value_name": self.value_name,
                })

        if not self.top_wineries:
            return self.render_template(
                "problem.html",
                problem_message="No data for this report.",
            )

        return self.render_template(
            "top_wineries_report.html",
            **self.to_template_kwargs(),
        )

    def to_template_kwargs(self):
        """
        :return: Dict with template arguments.
        """
        return {
            "top_wineries": self.top_wineries,
        }
