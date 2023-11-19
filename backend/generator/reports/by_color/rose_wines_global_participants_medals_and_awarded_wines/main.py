from generator.reports.continents_tab_report import ContinentsTabReport
from generator.enum import WineColor


class RoseWinesGlobalParticipantsMedalsAndAwardedWines(ContinentsTabReport):
    @property
    def title(self):
        return "4.2.3 Rose Wines: Global participants, Medals and Awarded wines"

    @property
    def weight(self):
        return 85

    def get_query(self):
        return self.build_query_for_count_wineries_medals_wines_by_continent(
            event_year=(self.year_from, self.year_to),
            wine_color=WineColor.ROSE,
        )
