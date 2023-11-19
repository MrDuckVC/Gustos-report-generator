from sqlalchemy import Select

from generator.reports.country_report import CountryReport
from generator.enum import WineType
from generator.reports.top_wineries_report import TopWineriesReport


class CountrySparklingPearlWinesTopWineriesByMedalCountReport(TopWineriesReport, CountryReport):
    @property
    def value_name(self) -> str:
        return "Medals"

    def get_query(self) -> Select:
        return self.build_query_for_top_wineries_by_medal_count(
            event_year=(self.year_from, self.year_to),
            countries_ids=self.country,
            wine_type=(WineType.SPARKLING, WineType.PEARL),
        )

    @property
    def title(self) -> str:
        return "4.5 <Country>: Sparkling & Pearl Wines: Top Wineries by Medal Count"

    @property
    def weight(self) -> int:
        return 466
