from generator.enum import WineColor, GWMRUrlRatingType, WineType, GrapeVariety
from generator.reports.top_wines_report import TopWinesReport


class StillRoseSingleVarietyWinesTopWinesInTheWorldByGWMR(TopWinesReport):
    def get_url(self) -> str:
        return self.build_top_wines_url(
            event_year=(self.year_from, self.year_to),
            rating_type=GWMRUrlRatingType.BY_GWMR,
            wine_type=WineType.STILL,
            wine_color=WineColor.ROSE,
            grape_variety=GrapeVariety.SINGLE,
        )

    @property
    def title(self) -> str:
        return "4.3.1 Still Rose Single variety wines: Top wines in the world by GWMR"


    @property
    def weight(self) -> int:
        return 106
