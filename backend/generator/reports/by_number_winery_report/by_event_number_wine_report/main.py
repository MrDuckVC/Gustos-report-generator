from sqlalchemy import func, select

from generator.reports.by_number_winery_report.by_number_winery_report import \
    ByNumberWineryReport
from gustos.models import (
    wine, wine_entity,
    award, award_wine_entity,
    event, winery,
)


class ByEventNumberWineryReport(ByNumberWineryReport):
    @property
    def title(self):
        return "8.1 Your Winery Position by number of different Competition Events"

    @property
    def parameter_title(self):
        return "Different Competitions"

    @property
    def weight(self):
        return 50

    def format_entity_value(self, value):
        return value

    def get_query(self):
        v = winery.alias("v")
        we = wine_entity.alias("we")
        w = wine.alias("w")
        awe = award_wine_entity.alias("awe")
        a = award.alias("a")
        e = event.alias("e")

        criteria = func.count(a.c.event_id.distinct())

        # Works slowly due to count distinct.
        return select(
            # 0  world_rank_index
            func.rank().over(order_by=criteria.desc()).label('world_rank'),
            # 1  world_percent_rank_index
            func.percent_rank().over(order_by=criteria.desc()).label('world_percent_rank'),
            # 2  continent_rank_index
            func.rank().over(order_by=criteria.desc(), partition_by=self.build_continent_case(v.c.country)).label('continent_rank'),
            # 3  continent_percent_rank_index
            func.percent_rank().over(order_by=criteria.desc(), partition_by=self.build_continent_case(v.c.country)).label('continent_percent_rank'),
            # 4  continent_id_index
            self.build_continent_case(v.c.country).label('continent_id'),
            # 5  country_rank_index
            func.rank().over(order_by=criteria.desc(), partition_by=v.c.country).label('country_rank'),
            # 6  country_percent_rank_index
            func.percent_rank().over(order_by=criteria.desc(), partition_by=v.c.country).label('country_percent_rank'),
            # 7  country_id_index
            v.c.country.label('country_id'),
            # 8  entity_name_index
            v.c.name.label('entity_name'),
            # 9  entity_value_index
            criteria.label('entity_value'),
            # 10 entity_id_index
            v.c.id.label('entity_id'),
        ).select_from(v) \
            .join(w, w.c.winery == v.c.id) \
            .join(we, we.c.wine == w.c.id) \
            .join(awe, awe.c.wine_entity_id == we.c.id) \
            .join(a, a.c.id == awe.c.award_id) \
            .join(e, e.c.id == a.c.event_id) \
            .where(e.c.year.between(self.year_from, self.year_to)) \
            .group_by(v.c.id) \
            .order_by(criteria.desc())
