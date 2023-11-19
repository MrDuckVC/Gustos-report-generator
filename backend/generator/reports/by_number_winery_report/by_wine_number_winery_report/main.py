from generator.reports.by_number_winery_report.by_number_winery_report import \
    ByNumberWineryReport


class ByWineNumberWineryReport(ByNumberWineryReport):
    @property
    def title(self):
        return "8.1 Your Winery Position by number of Total awarded wines"

    @property
    def parameter_title(self):
        return "Total awarded wines"

    @property
    def weight(self):
        return 70

    def format_entity_value(self, value):
        return value

    def get_query(self):
        return self._build_query_count_wine_entities_of_winery(
            event_year=(self.year_from, self.year_to),
        )
