from generator.reports.by_number_winery_report.by_number_winery_report import \
    ByNumberWineryReport


class ByAwardNumberWineryReport(ByNumberWineryReport):
    @property
    def title(self):
        return "8.1 Your Winery Position by Total number of medals"

    @property
    def parameter_title(self):
        return "Total Number of Medals"

    @property
    def weight(self):
        return 10

    def format_entity_value(self, value):
        return value

    def get_query(self):
        return self._build_query_count_awards_of_winery(
            event_year=(self.year_from, self.year_to)
        )
