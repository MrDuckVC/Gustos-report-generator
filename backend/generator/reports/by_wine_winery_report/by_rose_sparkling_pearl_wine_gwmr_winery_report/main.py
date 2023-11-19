from generator.reports.by_wine_winery_report.by_wine_winery_report import (
    ByWineWineryReport, WineRatingCriteria)
from generator.enum import WineType, WineColor


class ByRoseSparklingPearlWineGWMRWineryReport(ByWineWineryReport):
    @property
    def title(self):
        return "8.2 Your Best Rose Sparkling & Pearl Wine Position by GWMR score"

    @property
    def parameter_title(self):
        return "Best Rose Sparkling & Pearl GWMR Score"

    @property
    def weight(self):
        return 170

    def format_entity_value(self, value):
        if value is None:
            return None
        return round(value, 2)

    def get_query(self):
        return self._build_query_get_winery_rating_by_wine(
            rating_criteria=WineRatingCriteria.GWMR,
            wine_color=WineColor.ROSE,
            wine_type=(WineType.SPARKLING, WineType.PEARL),
        )
