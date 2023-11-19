from generator.enum import WineColor, GWMRUrlRatingType
from generator.reports.top_wines_report import TopWinesReport


class WhiteWinesTopWinesInTheWorldByGwmr(TopWinesReport):
    def get_url(self) -> str:
        return self.build_top_wines_url(
            event_year=(self.year_from, self.year_to),
            rating_type=GWMRUrlRatingType.BY_GWMR,
            wine_color=WineColor.WHITE,
        )

    @property
    def title(self) -> str:
        return "4.2.2 White Wines: Top wines in the world by GWMR"

    @property
    def weight(self) -> int:
        return 43
