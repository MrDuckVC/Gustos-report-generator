from sqlalchemy import Select

from generator.enum import WineColor
from generator.reports.top_wineries_report import TopWineriesReport


class RoseWinesTopWineriesInTheWorldByMedalCount(TopWineriesReport):
    @property
    def value_name(self) -> str:
        return "Medals"

    def get_query(self) -> Select:
        return self.build_query_for_top_wineries_by_medal_count(
            event_year=(self.year_from, self.year_to),
            wine_color=WineColor.ROSE,
        )

    @property
    def title(self) -> str:
        return "4.2.1 Rose Wines: Top Wineries in the World by Medal Count"


    @property
    def weight(self) -> int:
        return 66
