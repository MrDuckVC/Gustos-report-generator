from generator.reports.by_wine_winery_report.by_wine_winery_report import (
    ByWineWineryReport, WineRatingCriteria)


class ByWineAwardsWineryReport(ByWineWineryReport):
    @property
    def title(self):
        return "8.2 Your Best Wine Position by Total number of medals"

    @property
    def parameter_title(self):
        return "Best wine Number of Medals"

    @property
    def weight(self):
        return 20

    def format_entity_value(self, value):
        if value is None:
            return None
        return int(value)

    def get_query(self):
        return self._build_query_get_winery_rating_by_wine(
            rating_criteria=WineRatingCriteria.AWARDS,
        )
