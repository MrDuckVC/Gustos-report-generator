from sqlalchemy import Select

from generator.reports.continents_tab_report import ContinentsTabReport
from generator.enum import WineType, WineColor


class MostAwardedYearsOfHarvestForWhiteStillWines(ContinentsTabReport):
    @property
    def title(self):
        return "4.4 Most awarded years of harvest for White Still wines"

    @property
    def weight(self):
        return 13

    @property
    def use_tab_title(self) -> bool:
        return True

    def get_query(self) -> Select:
        return self.build_query_for_most_awarded_vintage_by_continent(
            event_year=(self.year_from, self.year_to),
            wine_color=WineColor.WHITE,
            wine_type=WineType.STILL,
        )
