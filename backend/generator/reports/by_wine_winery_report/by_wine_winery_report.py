from abc import ABC
from enum import Enum
from typing import Tuple

from sqlalchemy import func, select

from generator.exceptions import DataNotFoundException, RatingNotFoundException
from generator.enum import WineType, WineColor, GrapeVariety, Continent
from generator.reports.table_winery_report import TableWineryReport
from generator.utils.formatting import (
    format_entity_name,
    format_percent_rank, format_vintage,
)
from gustos.models import (
    file_managed, wine, wine_entity,
    award, award_wine_entity,
    event, wine_gwmr, winery,
)
from gustos.utils.file_managed import get_absolute_url


class WineRatingCriteria(Enum):
    GWMR = "GWMR"
    AWARDS = "AWARDS"


class ByWineWineryReport(TableWineryReport, ABC):
    def format_entity_name(self, name):
        if name is None:
            return None
        return f"{format_entity_name(name[0])} {format_entity_name(name[1])}", format_vintage(name[2])

    def get_template_kwargs(self):
        w = wine.alias("w")
        we = wine_entity.alias("we")
        fm = file_managed.alias("fm")

        query = select(
            func.json_value(w.c.category, "$.color"),
            fm.c.uri,
        ).select_from(w) \
            .join(we, we.c.wine == w.c.id) \
            .join(fm, fm.c.fid == we.c.photo, isouter=True) \
            .where(we.c.id == self.current_row[13])
        with self.database.connect() as connection:
            result = connection.execute(query)
            wine_color, wine_photo = result.fetchone()

        if wine_color is not None:
            wine_color = WineColor(int(wine_color)).name

        return {
            'wine_color': wine_color,
            'wine_photo': get_absolute_url(wine_photo),
        }

    def render(self, throw_exception=False):
        self.fill_continent_and_country()

        with self.database.connect() as connection:
            try:
                result = connection.execute(self.get_query())
                self.get_ratings_by_query_result(
                    result,
                    *self.__get_query_get_winery_rating_by_wine_indices(self.continent_id, self.country_id, self.winery_id),
                )
            except DataNotFoundException as e:
                wg = wine_gwmr.alias('wg')
                query = select(wg).select_from(wg).where(wg.c.year_from == self.year_from, wg.c.year_to == self.year_to)
                result = connection.execute(query)
                if not result.fetchone():
                    raise RatingNotFoundException() from e
                raise e

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
            "report8.2.html",
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

    def _build_query_get_winery_rating_by_wine(
            self,
            rating_criteria: WineRatingCriteria,
            wine_color: Tuple[WineColor, ...] | WineColor = None,
            wine_type: Tuple[WineType, ...] | WineType = None,
            grape_variety: GrapeVariety = None,
    ):
        v1 = winery.alias("v1")
        w2 = wine.alias("w2")
        we2 = wine_entity.alias("we2")
        we1 = self.build_query_for_wine_entity(
            select_fields=(
                w2.c.winery,
                w2.c.name,
                we2,
            ),
            wine_color=wine_color,
            wine_type=wine_type,
            grape_variety=grape_variety,
            w=w2,
            we=we2,
        ).alias('we1')

        if rating_criteria == WineRatingCriteria.GWMR:
            wg1 = wine_gwmr.alias("wg1")
            criteria = wg1.c.rating
        elif rating_criteria == WineRatingCriteria.AWARDS:
            awe1 = award_wine_entity.alias("awe1")
            criteria = func.count(awe1.c.award_id)

        query = select(
            # 0  world_rank_index
            func.rank().over(order_by=criteria.desc()).label('world_rank'),
            # 1  world_percent_rank_index
            func.percent_rank().over(order_by=criteria.desc()).label('world_percent_rank'),
            # 2  continent_rank_index
            func.rank().over(order_by=criteria.desc(), partition_by=self.build_continent_case(v1.c.country)).label('continent_rank'),
            # 3  continent_percent_rank_index
            func.percent_rank().over(order_by=criteria.desc(), partition_by=self.build_continent_case(v1.c.country)).label('continent_percent_rank'),
            # 4  continent_id_index
            self.build_continent_case(v1.c.country).label('continent_id'),
            # 5  country_rank_index
            func.rank().over(order_by=criteria.desc(), partition_by=v1.c.country).label('country_rank'),
            # 6  country_percent_rank_index
            func.percent_rank().over(order_by=criteria.desc(), partition_by=v1.c.country).label('country_percent_rank'),
            # 7  country_id_index
            v1.c.country.label('country_id'),
            # 8  entity_name_index
            v1.c.name.label('entity_name_1'),
            # 9  entity_name_index
            we1.c.name.label('entity_name_2'),
            # 10 entity_name_index
            we1.c.vintage.label('entity_name_3'),
            # 11 entity_value_index
            criteria.label('entity_value'),
            # 12 entity_id_index
            v1.c.id.label('entity_id'),
            # 13
            we1.c.id.label('wine_entity_id'),
        ).select_from(v1) \
            .join(we1, we1.c.winery == v1.c.id) \
            .order_by(criteria.desc()) \
            .group_by(we1.c.id)

        if rating_criteria == WineRatingCriteria.GWMR:
            query = query \
                .join(wg1, wg1.c.wine_entity_id == we1.c.id) \
                .where(
                    wg1.c.year_from == self.year_from,
                    wg1.c.year_to == self.year_to,
                    we1.c.gwmr.is_not(None),
                    we1.c.gwmr != 0,
                )
        else:
            a1 = award.alias("a1")
            e2 = event.alias("e2")

            query = query \
                .join(awe1, awe1.c.wine_entity_id == we1.c.id) \
                .join(a1, a1.c.id == awe1.c.award_id) \
                .join(e2, e2.c.id == a1.c.event_id) \
                .where(e2.c.year.between(self.year_from, self.year_to))

        return query

    @staticmethod
    def __get_query_get_winery_rating_by_wine_indices(continent_id: Continent, country_id: int, entity_id: int):
        return 0, 1, 2, 3, 4, continent_id, 5, 6, 7, country_id, (8, 9, 10), 11, 12, entity_id
