from sqlalchemy import func, select

from generator.reports.by_number_winery_report.by_number_winery_report import \
    ByNumberWineryReport
from generator.enum import AwardValue

from gustos.models import (
    wine, wine_entity,
    award, award_wine_entity,
    event, winery,
)


class ByGEGoldAwardRatioWineryReport(ByNumberWineryReport):
    @property
    def title(self):
        return "8.1 Your Winery Position by ratio of Gold and Grand Gold medals"

    @property
    def parameter_title(self):
        return "Gold and Grand ratio"

    @property
    def weight(self):
        return 30

    def format_entity_value(self, value):
        return value

    def get_query(self):
        v = winery.alias("v")
        we = wine_entity.alias("we")
        w = wine.alias("w")
        awe = award_wine_entity.alias("awe")
        a = award.alias("a")
        e = event.alias("e")

        criteria = func.round(func.sum(func.if_(a.c.value.in_((AwardValue.GRAND_GOLD.value, AwardValue.GOLD.value)), 1, 0)) / func.count(a.c.id) * 100, 2)

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
            func.concat(criteria, '%').label('entity_value'),  # 9  entity_value_index
            v.c.id.label('entity_id'),  # 10 entity_id_index
        ).select_from(v) \
            .join(w, w.c.winery == v.c.id) \
            .join(we, we.c.wine == w.c.id) \
            .join(awe, awe.c.wine_entity_id == we.c.id) \
            .join(a, a.c.id == awe.c.award_id) \
            .join(e, e.c.id == a.c.event_id) \
            .where(e.c.year.between(self.year_from, self.year_to)) \
            .group_by(v.c.id) \
            .order_by(criteria.desc())

        return query
