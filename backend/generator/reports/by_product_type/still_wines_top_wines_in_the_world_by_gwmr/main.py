from generator.enum import WineType, GWMRUrlRatingType
from generator.reports.top_wines_report import TopWinesReport


class StillWinesTopWinesInTheWorldByGwmr(TopWinesReport):
    def get_url(self) -> str:
        return self.build_top_wines_url(
            event_year=(self.year_from, self.year_to),
            rating_type=GWMRUrlRatingType.BY_GWMR,
            wine_type=WineType.STILL,
        )

    @property
    def title(self) -> str:
        return "4.1.1 Still Wines: Top wines in the world by GWMR"


    @property
    def weight(self) -> int:
        return 40
