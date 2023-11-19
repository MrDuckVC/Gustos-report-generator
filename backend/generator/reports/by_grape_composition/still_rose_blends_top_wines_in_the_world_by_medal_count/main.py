from generator.enum import WineColor, GWMRUrlRatingType, WineType, GrapeVariety
from generator.reports.top_wines_report import TopWinesReport


class StillRoseBlendsTopWinesInTheWorldByMedalCount(TopWinesReport):
    def get_url(self) -> str:
        return self.build_top_wines_url(
            event_year=(self.year_from, self.year_to),
            rating_type=GWMRUrlRatingType.BY_MEDALS,
            wine_type=WineType.STILL,
            wine_color=WineColor.ROSE,
            grape_variety=GrapeVariety.BLEND,
        )

    @property
    def title(self) -> str:
        return "4.3.3 Still Rose Blends: Top wines in the world by Medal Count"


    @property
    def weight(self) -> int:
        return 76
