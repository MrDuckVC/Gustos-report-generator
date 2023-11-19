from typing import Any

from sqlalchemy import func, select, Select

from generator.reports.continent_report import ContinentReport
from generator.reports.histogram_report import HistogramReport
from gustos.models import wine, taxonomy_term, award_wine_entity


class ContinentAverageRatingForTopCountriesReport(HistogramReport, ContinentReport):
    @property
    def title(self) -> str:
        return "4.5 <Continent>: Average rating for Top 6 Countries"

    @property
    def weight(self) -> int:
        return 40

    @property
    def get_query_args(self) -> dict[Any, str]:
        we_subquery = self.build_query_for_wine_entity(
            countries=self.CONTINENTS[self.continent],
            gwmr=(60.0, None),
            event_year=(self.year_from, self.year_to),
        ).alias("we_subquery")

        query = select(
            wine.c.country,
            taxonomy_term.c.name,
        ).select_from(award_wine_entity) \
            .join(we_subquery, we_subquery.c.id == award_wine_entity.c.wine_entity_id) \
            .join(wine, wine.c.id == we_subquery.c.wine) \
            .join(taxonomy_term, taxonomy_term.c.tid == wine.c.country) \
            .group_by(wine.c.country) \
            .order_by(func.count(award_wine_entity.c.award_id).desc())

        with self.database.connect() as connection:
            result = {}
            for country_id, country_name in connection.execute(query):
                result[country_id] = country_name

        return result

    def get_query(self, argument) -> Select:
        return self.build_query_by_wine_entity(
            countries=argument,
        )
