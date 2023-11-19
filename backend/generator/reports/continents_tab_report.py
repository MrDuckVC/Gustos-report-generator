from abc import abstractmethod
from typing import Tuple, Any

from django.http import HttpRequest
from sqlalchemy import Select, func, distinct, select

from generator.reports.report import Report
from generator.enum import WineType, WineColor, GrapeVariety, Continent
from generator.utils.database import apply_range_filter
from gustos.models import (
    wine, wine_grapes, taxonomy_term,
    award_wine_entity, winery, wine_entity,
    award, event,
)


class ContinentsTabReport(Report):
    def __init__(
            self,
            request: HttpRequest,
    ):
        super().__init__(request)

        self.africa_tab: dict = {}
        """Dictionary where keys are names of parameters and values are values of parameters of Africa table."""
        self.asia_tab: dict = {}
        """Dictionary where keys are names of parameters and values are values of parameters of Asia table."""
        self.europe_tab: dict = {}
        """Dictionary where keys are names of parameters and values are values of parameters of Europe table."""
        self.north_america_tab: dict = {}
        """Dictionary where keys are names of parameters and values are values of parameters of North America table."""
        self.pacific_tab: dict = {}
        """Dictionary where keys are names of parameters and values are values of parameters of Pacific table."""
        self.south_america_tab: dict = {}
        """Dictionary where keys are names of parameters and values are values of parameters of South America table."""

        self.africa_tab_name: str | None = None
        """This name will be used as name of Africa table."""
        self.asia_tab_name: str | None = None
        """This name will be used as name of Asia table."""
        self.europe_tab_name: str | None = None
        """This name will be used as name of Europe table."""
        self.north_america_tab_name: str | None = None
        """This name will be used as name of North America table."""
        self.pacific_tab_name: str | None = None
        """This name will be used as name of Pacific table."""
        self.south_america_tab_name: str | None = None
        """This name will be used as name of South America table."""

    @property
    def continent_column_name(self) -> str:
        """
        :return: Index of column which contains name of continent.
        """
        return "CONTINENT"

    @property
    def tab_title_column_name(self) -> str:
        """
        :return: Index of column which contains name of continent.
        """
        return "TAB_TITLE"

    @property
    # @abstractmethod
    def use_tab_title(self) -> bool:
        """
        :return: True if tab title should be used, False otherwise.
        """
        return False

    @abstractmethod
    def get_query(self) -> Select:
        """
        :return: SQLAlchemy query object.
        """
        pass

    def build_query_for_count_wineries_medals_wines_by_continent(
            self,
            select_fields: Tuple[Any, ...] = None,
            wine_color: Tuple[WineColor, ...] | WineColor = None,
            wine_type: Tuple[WineType, ...] | WineType = None,
            grape_variety: GrapeVariety = None,
            event_year: Tuple[int, int] = None,
    ) -> Select:
        """
        :return: SQLAlchemy query object.
        """
        we_subquery = self.build_query_for_wine_entity(
            wine_color=wine_color,
            wine_type=wine_type,
            grape_variety=grape_variety,
            event_year=event_year,
        ).alias("we_subquery")

        if select_fields is None:
            select_fields = (
                func.count(distinct(winery.c.id)).label("MANUFACTURES"),
                func.count(distinct(award_wine_entity.c.wine_entity_id)).label("MEDAL WINES"),
                func.count(award_wine_entity.c.award_id).label("MEDALS"),
                self.build_continent_case(winery.c.country).label(self.continent_column_name),
            )

        query = apply_range_filter(
            select(
                *select_fields
            ).select_from(award_wine_entity) \
                .join(award, award.c.id == award_wine_entity.c.award_id) \
                .join(event, event.c.id == award.c.event_id) \
                .join(we_subquery, we_subquery.c.id == award_wine_entity.c.wine_entity_id) \
                .join(wine, wine.c.id == we_subquery.c.wine) \
                .join(winery, winery.c.id == wine.c.winery) \
                .where(
                    winery.c.country.is_not(None),
                ),
            event.c.year,
            event_year,
        )

        return query.group_by(
            self.continent_column_name
        )

    def build_query_for_best_grape_varieties_by_continent(
            self,
            wine_color: Tuple[WineColor, ...] | WineColor = None,
            wine_type: Tuple[WineType, ...] | WineType = None,
            grape_variety: GrapeVariety = None,
            event_year: Tuple[int, int] = None,
    ) -> Select:
        we_subquery = self.build_query_for_wine_entity(
            wine_color=wine_color,
            wine_type=wine_type,
            grape_variety=grape_variety,
            event_year=event_year,
        ).alias("we_subquery")

        position_label = "POSITION"
        award_count_label = "MEDALS"

        subquery = apply_range_filter(
            select(
                taxonomy_term.c.name.label(self.tab_title_column_name),
                func.count(award_wine_entity.c.award_id).label(award_count_label),
                self.build_continent_case(wine.c.country).label(self.continent_column_name),
                func.rank().over(
                    partition_by=self.build_continent_case(wine.c.country),
                    order_by=func.count(award_wine_entity.c.award_id).desc()
                ).label(position_label)
            ).select_from(wine_grapes) \
                .join(we_subquery, wine_grapes.c.wine_entity == we_subquery.c.id) \
                .join(wine, we_subquery.c.wine == wine.c.id) \
                .join(award_wine_entity, award_wine_entity.c.wine_entity_id == we_subquery.c.id) \
                .join(award, award.c.id == award_wine_entity.c.award_id) \
                .join(event, event.c.id == award.c.event_id) \
                .join(taxonomy_term, taxonomy_term.c.tid == wine_grapes.c.grape) \
                .group_by(
                wine_grapes.c.grape,
                self.continent_column_name,
            ).order_by(
                position_label,
            ),
            event.c.year,
            event_year,
        )

        query = select(
            getattr(subquery.c, self.tab_title_column_name),
            getattr(subquery.c, award_count_label),
            getattr(subquery.c, self.continent_column_name),
        ).select_from(
            subquery
        ).where(
            getattr(subquery.c, position_label) == 1
        )

        return query

    def build_query_for_most_awarded_vintage_by_continent(
            self,
            wine_color: Tuple[WineColor, ...] | WineColor = None,
            wine_type: Tuple[WineType, ...] | WineType = None,
            grape_variety: GrapeVariety = None,
            event_year: Tuple[int, int] = None,
    ) -> Select:
        position_label = "POSITION"
        award_count_label = "MEDALS"

        we = wine_entity.alias("we")
        w = wine.alias("w")

        subquery = apply_range_filter(
            self.build_query_for_wine_entity(
                select_fields=(
                    we.c.vintage.label(self.tab_title_column_name),
                    func.count(award_wine_entity.c.award_id).label(award_count_label),
                    self.build_continent_case(w.c.country).label(self.continent_column_name),
                    func.rank().over(
                        partition_by=self.build_continent_case(w.c.country),
                        order_by=func.count(award_wine_entity.c.award_id).desc()
                    ).label(position_label)
                ),
                wine_color=wine_color,
                wine_type=wine_type,
                grape_variety=grape_variety,
                event_year=event_year,
                we=we,
                w=w,
            ) \
                .join(award_wine_entity, award_wine_entity.c.wine_entity_id == we.c.id) \
                .join(award, award.c.id == award_wine_entity.c.award_id) \
                .join(event, event.c.id == award.c.event_id) \
                .group_by(
                    we.c.vintage,
                    self.continent_column_name,
                ) \
                .order_by(
                    position_label,
                ),
            event.c.year,
            event_year,
        )

        return select(
            getattr(subquery.c, self.tab_title_column_name),
            getattr(subquery.c, award_count_label),
            getattr(subquery.c, self.continent_column_name),
        ).select_from(
            subquery
        ).where(
            getattr(subquery.c, position_label) == 1
        )

    def render(self):
        query = self.get_query()

        with self.database.connect() as connection:
            result = connection.execute(query).mappings()
            for row in result:
                params = list(row.keys())
                params.remove(self.continent_column_name)
                try:
                    if self.use_tab_title:
                        params.remove(self.tab_title_column_name)
                        setattr(self, f"{Continent(int(row[self.continent_column_name])).name.lower()}_tab_name", str(row[self.tab_title_column_name]))
                    for param in params:
                        getattr(self, f"{Continent(int(row[self.continent_column_name])).name.lower()}_tab")[param] = row[param]
                except ValueError:
                    pass

        return self.render_template(
            "continents_tab_report.html",
            **self.to_template_kwargs()
        )

    def to_template_kwargs(self) -> dict:
        """
        :return: Dictionary which will be passed as keyword arguments to the render_template function.
        """

        return {
            "north_america_tab": self.north_america_tab.items(),
            "south_america_tab": self.south_america_tab.items(),
            "europe_tab": self.europe_tab.items(),
            "asia_tab": self.asia_tab.items(),
            "africa_tab": self.africa_tab.items(),
            "pacific_tab": self.pacific_tab.items(),
            "north_america_tab_name": self.north_america_tab_name,
            "south_america_tab_name": self.south_america_tab_name,
            "europe_tab_name": self.europe_tab_name,
            "asia_tab_name": self.asia_tab_name,
            "africa_tab_name": self.africa_tab_name,
            "pacific_tab_name": self.pacific_tab_name,
        }

