from generator.reports.by_number_winery_report.by_number_winery_report import \
    ByNumberWineryReport
from generator.enum import AwardValue


class ByGEGoldAwardNumberWineryReport(ByNumberWineryReport):
    @property
    def title(self):
        return "8.1 Your Winery Position by number of Gold and Grand Gold medals"

    @property
    def parameter_title(self):
        return "Gold and Grand Medals"

    @property
    def weight(self):
        return 20

    def format_entity_value(self, value):
        return value

    def get_query(self):
        return self._build_query_count_awards_of_winery(
            event_year=(self.year_from, self.year_to),
            award_value=(AwardValue.GRAND_GOLD, AwardValue.GOLD)
        )
