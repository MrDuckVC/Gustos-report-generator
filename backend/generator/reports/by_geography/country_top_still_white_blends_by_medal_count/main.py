from generator.reports.country_report import CountryReport
from generator.enum import WineColor, GWMRUrlRatingType, WineType, GrapeVariety
from generator.reports.top_wines_report import TopWinesReport


class CountryTopStillWhiteBlendsByMedalCountReport(TopWinesReport, CountryReport):
    def get_url(self) -> str:
        return self.build_top_wines_url(
            event_year=(self.year_from, self.year_to),
            rating_type=GWMRUrlRatingType.BY_MEDALS,
            wine_color=WineColor.WHITE,
            wine_type=WineType.STILL,
            grape_variety=GrapeVariety.BLEND,
            countries_ids=self.country,
        )

    @property
    def title(self) -> str:
        return "4.5.2 <Country>: Top Still White Blends by Medal Count"

    @property
    def weight(self) -> int:
        return 456
