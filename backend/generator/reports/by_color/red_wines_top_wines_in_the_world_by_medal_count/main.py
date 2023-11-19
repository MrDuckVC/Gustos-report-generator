from generator.enum import WineColor, GWMRUrlRatingType
from generator.reports.top_wines_report import TopWinesReport


class RedWinesTopWinesInTheWorldByMedalCount(TopWinesReport):
    def get_url(self) -> str:
        return self.build_top_wines_url(
            event_year=(self.year_from, self.year_to),
            rating_type=GWMRUrlRatingType.BY_MEDALS,
            wine_color=WineColor.RED,
        )

    @property
    def title(self) -> str:
        return "4.2.1 Red Wines: Top wines in the world by Medal Count"


    @property
    def weight(self) -> int:
        return 50
