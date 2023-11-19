from sqlalchemy import Select, func, select, distinct

from generator.reports.continents_value_report import ContinentsValueReport
from gustos.models import wine_grapes, wine, award_wine_entity


class NumberOfAwardedGrapeVarietiesPerRegion(ContinentsValueReport):
    @property
    def title(self) -> str:
        return "4.3.2 Number of awarded grape varieties per region"

    def get_query(self) -> Select:
        we_subquery = self.build_query_for_wine_entity(
            event_year=(self.year_from, self.year_to),
        ).alias("we_subquery")

        return select(
                func.count(distinct(wine_grapes.c.grape)).label(self.value_column_name),
                self.build_continent_case(wine.c.country).label(self.continent_column_name),
            ).select_from(award_wine_entity) \
                .join(we_subquery, we_subquery.c.id == award_wine_entity.c.wine_entity_id) \
                .join(wine, wine.c.id == we_subquery.c.wine) \
                .join(wine_grapes, wine_grapes.c.wine_entity == we_subquery.c.id) \
            .group_by(self.continent_column_name)



    @property
    def weight(self) -> int:
        return 140