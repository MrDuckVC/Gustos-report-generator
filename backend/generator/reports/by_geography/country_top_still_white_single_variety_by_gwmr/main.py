from generator.reports.country_report import CountryReport
from generator.enum import WineColor, GWMRUrlRatingType, WineType, GrapeVariety
from generator.reports.top_wines_report import TopWinesReport


class CountryTopStillWhiteSingleVarietyByGwmrReport(TopWinesReport, CountryReport):
    def get_url(self) -> str:
        return self.build_top_wines_url(
            event_year=(self.year_from, self.year_to),
            rating_type=GWMRUrlRatingType.BY_GWMR,
            wine_color=WineColor.WHITE,
            wine_type=WineType.STILL,
            grape_variety=GrapeVariety.SINGLE,
            countries_ids=self.country,
        )

    @property
    def title(self) -> str:
        return "4.5.2 <Country>: Top Still White Single Variety by GWMR"

    @property
    def weight(self) -> int:
        return 460
