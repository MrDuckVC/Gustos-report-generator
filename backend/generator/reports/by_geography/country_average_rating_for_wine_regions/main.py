from typing import Any

from sqlalchemy import func, select, Select

from generator.reports.country_report import CountryReport
from generator.reports.histogram_report import HistogramReport
from gustos.models import wine_entity, wine, taxonomy_term, award_wine_entity


class CountryAverageRatingForWineRegionsReport(HistogramReport, CountryReport):
    @property
    def title(self) -> str:
        return "4.5 <Country>: Average rating for Wine Regions"

    @property
    def weight(self) -> int:
        return 360

    @property
    def get_query_args(self) -> dict[Any, str]:
        we_subquery = self.build_query_for_wine_entity(
            countries=self.country,
            gwmr=(60.0, None),
            event_year=(self.year_from, self.year_to),
        ).alias("we_subquery")

        query = select(
            taxonomy_term.c.tid,
            taxonomy_term.c.name,
        ).select_from(award_wine_entity) \
            .join(we_subquery, we_subquery.c.id == award_wine_entity.c.wine_entity_id) \
            .join(wine, wine.c.id == we_subquery.c.wine) \
            .join(taxonomy_term, taxonomy_term.c.tid == we_subquery.c.region) \
            .group_by(taxonomy_term.c.tid) \
            .order_by(func.count(award_wine_entity.c.award_id).desc())

        with self.database.connect() as connection:
            result = {}
            for region_id, region_name in connection.execute(query):
                result[region_id] = region_name

        return result

    def get_query(self, argument) -> Select:
        return self.build_query_by_wine_entity(
            countries=self.country,
            we=wine_entity
        ).where(
            wine_entity.c.region == argument,
        )
