from generator.reports.by_number_winery_report.by_number_winery_report import \
    ByNumberWineryReport
from generator.enum import WineType


class ByRoseSparklingPearlNumberWineryReport(ByNumberWineryReport):
    @property
    def title(self):
        return "8.1 Your Winery Position by number of awarded Rose Sparkling & Pearl"

    @property
    def parameter_title(self):
        return "Awarded Rose Sparkling & Pearl"

    @property
    def weight(self):
        return 150

    def format_entity_value(self, value):
        return value

    def get_query(self):
        return self._build_query_count_wine_entities_of_winery(
            event_year=(self.year_from, self.year_to),
            wine_type=(WineType.SPARKLING.value, WineType.PEARL.value)
        )
