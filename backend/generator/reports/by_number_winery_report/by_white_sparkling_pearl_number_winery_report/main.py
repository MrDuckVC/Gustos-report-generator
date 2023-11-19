from generator.reports.by_number_winery_report.by_number_winery_report import \
    ByNumberWineryReport
from generator.enum import WineType, WineColor


class ByWhiteSparklingPearlNumberWineryReport(ByNumberWineryReport):
    @property
    def title(self):
        return "8.1 Your Winery Position by number of awarded White Sparkling & Pearl"

    @property
    def parameter_title(self):
        return "Awarded White Sparkling & Pearl"

    @property
    def weight(self):
        return 140

    def format_entity_value(self, value):
        return value

    def get_query(self):
        return self._build_query_count_wine_entities_of_winery(
            event_year=(self.year_from, self.year_to),
            wine_color=WineColor.WHITE,
            wine_type=(WineType.SPARKLING, WineType.PEARL),
        )
