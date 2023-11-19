from abc import ABC
from typing import Sequence, Tuple

from sqlalchemy import func, select

from generator.enum import WineType, WineColor, GrapeVariety, Continent, AwardValue
from generator.reports.table_winery_report import TableWineryReport
from generator.utils.formatting import format_entity_name, format_percent_rank
from gustos.models import (
    wine, wine_entity,
    award, award_wine_entity,
    event, winery,
)


class ByNumberWineryReport(TableWineryReport, ABC):
    def format_entity_name(self, name):
        if name is None:
            return None
        return format_entity_name(name)

    def get_template_kwargs(self):
        return { }

    def render(self, throw_exception=False):
        self.fill_continent_and_country()

        with self.database.connect() as connection:
            result = connection.execute(self.get_query())
            self.get_ratings_by_query_result(
                result,
                *self.__get_query_count_wine_entities_of_winery_indices(self.continent_id, self.country_id, self.winery_id),
            )

        world_percent_rank = format_percent_rank(self.world_percent_rank)
        name_svg_world_rating = self.build_pie_chart_base64(
            x=world_percent_rank,
            color=self.determ_gr_color(limit=world_percent_rank),
        )

        continent_percent_rank = format_percent_rank(self.continent_percent_rank)
        name_svg_continent_rating = self.build_pie_chart_base64(
            x=continent_percent_rank,
            color=self.determ_gr_color(limit=continent_percent_rank),
        )

        country_percent_rank = format_percent_rank(self.country_percent_rank)
        name_svg_local_rating = self.build_pie_chart_base64(
            x=country_percent_rank,
            color=self.determ_gr_color(limit=country_percent_rank),
        )
        return self.render_template(
            "report8.1.html",
            report_title=self.title,
            report_parameter_title=self.parameter_title,
            continent_name=self.continent_name,
            country_name=self.country_name,
            year_from=self.year_from,
            year_to=self.year_to,
            name_svg_world_rating=name_svg_world_rating,
            name_svg_continent_rating=name_svg_continent_rating,
            name_svg_local_rating=name_svg_local_rating,
            **self.to_template_kwargs(),
        )

    def _build_query_count_wine_entities_of_winery(
            self,
            event_year: Tuple[int | None, int | None] = None,
            wine_color: Tuple[WineColor, ...] | WineColor = None,
            wine_type: Tuple[WineType, ...] | WineType = None,
            grape_variety: GrapeVariety = None,
            gwmr: Tuple[int | None, int | None] = None,
    ):
        v = winery.alias("v")
        w2 = wine.alias("w2")
        we2 = wine_entity.alias("we2")
        we1 = self.build_query_for_wine_entity(
            select_fields=(
                we2,
                w2.c.winery,
            ),
            event_year=event_year,
            wine_color=wine_color,
            wine_type=wine_type,
            grape_variety=grape_variety,
            gwmr=gwmr,
            we=we2,
            w=w2,
        ).alias('we1')

        query = select(
            # 0  world_rank_index
            func.rank().over(order_by=func.count(we1.c.id).desc()).label('world_rank'),
            # 1  world_percent_rank_index
            func.percent_rank().over(order_by=func.count(we1.c.id).desc()).label('world_percent_rank'),
            # 2  continent_rank_index
            func.rank().over(order_by=func.count(we1.c.id).desc(), partition_by=self.build_continent_case(v.c.country)).label('continent_rank'),
            # 3  continent_percent_rank_index
            func.percent_rank().over(order_by=func.count(we1.c.id).desc(), partition_by=self.build_continent_case(v.c.country)).label('continent_percent_rank'),
            # 4  continent_id_index
            self.build_continent_case(v.c.country).label('continent_id'),
            # 5  country_rank_index
            func.rank().over(order_by=func.count(we1.c.id).desc(), partition_by=v.c.country).label('country_rank'),
            # 6  country_percent_rank_index
            func.percent_rank().over(order_by=func.count(we1.c.id).desc(), partition_by=v.c.country).label('country_percent_rank'),
            # 7  country_id_index
            v.c.country.label('country_id'),
            # 8  entity_name_index
            v.c.name.label('entity_name'),
            # 9  entity_value_index
            func.count(we1.c.id).label('entity_value'),
            # 10 entity_id_index
            v.c.id.label('entity_id'),
        ).select_from(v) \
            .join(we1, we1.c.winery == v.c.id) \
            .group_by(v.c.id) \
            .order_by(
            func.count(we1.c.id).desc(),
            v.c.name,
            v.c.id
        )

        return query

    @staticmethod
    def __get_query_count_wine_entities_of_winery_indices(continent_id: Continent, country_id: int, entity_id: int):
        return 0, 1, 2, 3, 4, continent_id, 5, 6, 7, country_id, 8, 9, 10, entity_id

    def _build_query_count_awards_of_winery(
            self,
            event_year: Tuple[int | None, int | None] = None,
            award_value: Tuple[AwardValue | str, ...] = None,
    ):
        v = winery.alias("v")
        we = wine_entity.alias("we")
        w = wine.alias("w")
        awe = award_wine_entity.alias("awe")

        query = select(
            # 0  world_rank_index
            func.rank().over(order_by=func.count(awe.c.award_id).desc()).label('world_rank'),
            # 1  world_percent_rank_index
            func.percent_rank().over(order_by=func.count(awe.c.award_id).desc()).label('world_percent_rank'),
            # 2  continent_rank_index
            func.rank().over(order_by=func.count(awe.c.award_id).desc(), partition_by=self.build_continent_case(v.c.country)).label('continent_rank'),
            # 3  continent_percent_rank_index
            func.percent_rank().over(order_by=func.count(awe.c.award_id).desc(), partition_by=self.build_continent_case(v.c.country)).label('continent_percent_rank'),
            # 4  continent_id_index
            self.build_continent_case(v.c.country).label('continent_id'),
            # 5  country_rank_index
            func.rank().over(order_by=func.count(awe.c.award_id).desc(), partition_by=v.c.country).label('country_rank'),
            # 6  country_percent_rank_index
            func.percent_rank().over(order_by=func.count(awe.c.award_id).desc(), partition_by=v.c.country).label('country_percent_rank'),
            # 7  country_id_index
            v.c.country.label('country_id'),
            # 8  entity_name_index
            v.c.name.label('entity_name'),
            # 9  entity_value_index
            func.count(awe.c.award_id).label('entity_value'),
            # 10 entity_id_index
            v.c.id.label('entity_id'),
        ).select_from(v) \
            .join(w, w.c.winery == v.c.id) \
            .join(we, we.c.wine == w.c.id) \
            .join(awe, awe.c.wine_entity_id == we.c.id) \
            .group_by(v.c.id) \
            .order_by(func.count(awe.c.award_id).desc())

        if event_year is not None:
            a = award.alias("a")
            e = event.alias("e")
            query = query.join(a, a.c.id == awe.c.award_id) \
                .join(e, e.c.id == a.c.event_id)

            event_year_from, event_year_to = event_year
            if event_year_from is None:
                query = query.where(e.c.year <= event_year_to)
            elif event_year_to is None:
                query = query.where(e.c.year >= event_year_from)
            else:
                query = query.where(e.c.year.between(event_year_from, event_year_to))

        if award_value is not None:
            if not isinstance(award_value, Sequence):
                award_value = (award_value,)
            award_value = tuple((av.value if isinstance(av, AwardValue) else av for av in award_value))
            if len(award_value) > 0:
                # Means that an is not joined yet.
                if event_year is None:
                    query = query.join(a, a.c.id == awe.c.award_id)
                query = query.where(a.c.value.in_(award_value))

        return query
