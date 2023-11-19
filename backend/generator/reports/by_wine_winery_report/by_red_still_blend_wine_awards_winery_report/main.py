from generator.reports.by_wine_winery_report.by_wine_winery_report import (
    ByWineWineryReport, WineRatingCriteria)
from generator.enum import WineType, WineColor, GrapeVariety


class ByRedStillBlendWineAwardsWineryReport(ByWineWineryReport):
    @property
    def title(self):
        return "8.2 Your Best Red Still Blend Wine position by Total number of medals"

    @property
    def parameter_title(self):
        return "Best Red Still Blend Number of Medals"

    @property
    def weight(self):
        return 40

    def format_entity_value(self, value):
        if value is None:
            return None
        return int(value)

    def get_query(self):
        return self._build_query_get_winery_rating_by_wine(
            rating_criteria=WineRatingCriteria.AWARDS,
            wine_color=WineColor.RED,
            wine_type=WineType.STILL,
            grape_variety=GrapeVariety.BLEND,
        )
