from sqlalchemy import Select

from generator.reports.continents_tab_report import ContinentsTabReport
from generator.enum import WineType, WineColor


class ByGrapeVarietiesMostAwardedGrapesInRoseSparklingWines(ContinentsTabReport):
    @property
    def title(self):
        return "4.3.2 By Grape varieties: Most awarded grapes in Rose Sparkling wines"

    @property
    def weight(self):
        return 175

    @property
    def use_tab_title(self) -> bool:
        return True

    def get_query(self) -> Select:
        return self.build_query_for_best_grape_varieties_by_continent(
            event_year=(self.year_from, self.year_to),
            wine_color=WineColor.ROSE,
            wine_type=(WineType.SPARKLING, WineType.PEARL),
        )
