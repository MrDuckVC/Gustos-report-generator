from sqlalchemy import distinct, func, select

from generator.reports.by_number_winery_report.by_number_winery_report import \
    ByNumberWineryReport
from gustos.models import (
    wine, wine_entity,
    wine_grapes, award,
    award_wine_entity, event,
    winery,
)


class ByGrapeNumberWineryReport(ByNumberWineryReport):
    @property
    def title(self):
        return "8.1 Your Winery Position by Total number of grape varieties in awarded wines"

    @property
    def parameter_title(self):
        return "Total grape varieties"

    @property
    def weight(self):
        return 60

    def format_entity_value(self, value):
        return value

    def get_query(self):
        v = winery.alias("v")
        w = wine.alias("w")
        we = wine_entity.alias("we")
        wg = wine_grapes.alias("wg")
        awe2 = award_wine_entity.alias("awe1")
        a2 = award.alias("a")
        e2 = event.alias("e")

        criteria = func.count(distinct(wg.c.grape))

        subquery = select(awe2) \
            .select_from(awe2) \
            .join(a2, a2.c.id == awe2.c.award_id) \
            .join(e2, e2.c.id == a2.c.event_id) \
            .where(
                awe2.c.wine_entity_id == we.c.id,
                e2.c.year.in_((self.year_from, self.year_to)),
            )

        query = select(
            func.rank().over(order_by=criteria.desc()).label('world_rank'),  # 0  world_rank_index
            func.percent_rank().over(order_by=criteria.desc()).label('world_percent_rank'),  # 1  world_percent_rank_index
            func.rank().over(order_by=criteria.desc(), partition_by=self.build_continent_case(v.c.country)).label('continent_rank'),  # 2  continent_rank_index
            func.percent_rank().over(order_by=criteria.desc(), partition_by=self.build_continent_case(v.c.country)).label('continent_percent_rank'),  # 3  continent_percent_rank_index
            self.build_continent_case(v.c.country).label('continent_id'),  # 4  continent_id_index
            func.rank().over(order_by=criteria.desc(), partition_by=v.c.country).label('country_rank'),  # 5  country_rank_index
            func.percent_rank().over(order_by=criteria.desc(), partition_by=v.c.country).label('country_percent_rank'),  # 6  country_percent_rank_index
            v.c.country.label('country_id'),  # 7  country_id_index
            v.c.name.label('entity_name'),  # 8  entity_name_index
            criteria.label('entity_value'),  # 9  entity_value_index
            v.c.id.label('entity_id'),  # 10 entity_id_index
        ).select_from(v) \
            .join(w, w.c.winery == v.c.id) \
            .join(we, we.c.wine == w.c.id) \
            .join(wg, wg.c.wine_entity == we.c.id) \
            .where(subquery.exists()) \
            .group_by(v.c.id) \
            .order_by(criteria.desc())

        return query
