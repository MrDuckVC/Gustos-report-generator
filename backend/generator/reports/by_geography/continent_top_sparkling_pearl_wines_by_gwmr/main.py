from generator.reports.continent_report import ContinentReport
from generator.enum import GWMRUrlRatingType, WineType
from generator.reports.top_wines_report import TopWinesReport


class ContinentTopSparklingPearlWinesByGwmr(TopWinesReport, ContinentReport):
    def get_url(self) -> str:
        return self.build_top_wines_url(
            event_year=(self.year_from, self.year_to),
            rating_type=GWMRUrlRatingType.BY_GWMR,
            wine_type=(WineType.SPARKLING, WineType.PEARL),
            countries_ids=self.CONTINENTS[self.continent],
        )

    @property
    def title(self) -> str:
        return "4.5.1 <Continent>: Top Sparkling & Pearl Wines by GWMR"

    @property
    def weight(self) -> int:
        return 230
