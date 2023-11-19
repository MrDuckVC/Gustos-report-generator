from generator.reports.by_wine_winery_report.by_wine_winery_report import (
    ByWineWineryReport, WineRatingCriteria)
from generator.enum import WineType, WineColor, GrapeVariety


class ByRoseStillBlendWineGWMRWineryReport(ByWineWineryReport):
    @property
    def title(self):
        return "8.2 Your Best Rose Still Blend Wine Position by GWMR score"

    @property
    def parameter_title(self):
        return "Best Rose Still Blend GWMR Score"

    @property
    def weight(self):
        return 70

    def format_entity_value(self, value):
        if value is None:
            return None
        return round(value, 2)

    def get_query(self):
        return self._build_query_get_winery_rating_by_wine(
            rating_criteria=WineRatingCriteria.GWMR,
            wine_color=WineColor.ROSE,
            wine_type=WineType.STILL,
            grape_variety=GrapeVariety.BLEND,
        )
