from generator.reports.by_number_winery_report.by_number_winery_report import \
    ByNumberWineryReport
from generator.enum import WineType, WineColor, GrapeVariety


class ByRoseStillSingleVarietyNumberWineryReport(ByNumberWineryReport):
    @property
    def title(self):
        return "8.1 Your Winery Position by number of awarded Rose Still Single Variety"

    @property
    def parameter_title(self):
        return "Awarded Rose Still Single Variety"

    @property
    def weight(self):
        return 130

    def format_entity_value(self, value):
        return value

    def get_query(self):
        return self._build_query_count_wine_entities_of_winery(
            event_year=(self.year_from, self.year_to),
            wine_color=WineColor.ROSE,
            wine_type=WineType.STILL,
            grape_variety=GrapeVariety.SINGLE,
        )
