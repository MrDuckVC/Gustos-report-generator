from generator.reports.continent_report import ContinentReport
from generator.enum import WineColor, GWMRUrlRatingType, WineType, GrapeVariety
from generator.reports.top_wines_report import TopWinesReport


class ContinentTopStillWhiteSingleVarietyByGwmrReport(TopWinesReport, ContinentReport):
    def get_url(self) -> str:
        return self.build_top_wines_url(
            event_year=(self.year_from, self.year_to),
            rating_type=GWMRUrlRatingType.BY_GWMR,
            wine_color=WineColor.WHITE,
            wine_type=WineType.STILL,
            grape_variety=GrapeVariety.SINGLE,
            countries_ids=self.CONTINENTS[self.continent],
        )

    @property
    def title(self) -> str:
        return "4.5.2 <Continent>: Top Still White Single Variety by GWMR"

    @property
    def weight(self) -> int:
        return 193
