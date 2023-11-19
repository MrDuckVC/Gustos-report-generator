from sqlalchemy import Select

from generator.reports.continent_report import ContinentReport
from generator.enum import WineType, WineColor, GrapeVariety
from generator.reports.top_wineries_report import TopWineriesReport


class ContinentStillRedSingleVarietyTopWineriesByMedalCountReport(TopWineriesReport, ContinentReport):
    @property
    def value_name(self) -> str:
        return "Medals"

    def get_query(self) -> Select:
        return self.build_query_for_top_wineries_by_medal_count(
            event_year=(self.year_from, self.year_to),
            countries_ids=self.CONTINENTS[self.continent],
            wine_color=WineColor.RED,
            wine_type=WineType.STILL,
            grape_variety=GrapeVariety.SINGLE,
        )

    @property
    def title(self) -> str:
        return "4.5.1 <Continent>: Still Red Single Variety: Top Wineries by Medal Count"

    @property
    def weight(self) -> int:
        return 210
