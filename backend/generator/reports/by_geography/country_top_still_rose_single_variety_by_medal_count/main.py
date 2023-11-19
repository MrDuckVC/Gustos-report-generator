from generator.reports.country_report import CountryReport
from generator.enum import WineColor, GWMRUrlRatingType, WineType, GrapeVariety
from generator.reports.top_wines_report import TopWinesReport


class CountryTopStillRoseSingleVarietyByMedalCountReport(TopWinesReport, CountryReport):
    def get_url(self) -> str:
        return self.build_top_wines_url(
            event_year=(self.year_from, self.year_to),
            rating_type=GWMRUrlRatingType.BY_MEDALS,
            wine_color=WineColor.ROSE,
            wine_type=WineType.STILL,
            grape_variety=GrapeVariety.SINGLE,
            countries_ids=self.country,
        )

    @property
    def title(self) -> str:
        return "4.5.3 <Country>: Top Still Rose Single Variety by Medal Count"

    @property
    def weight(self) -> int:
        return 461
