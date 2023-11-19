from sqlalchemy import func, distinct, literal

from generator.reports.coefficient_report import CoefficientReport
from generator.reports.continents_tab_report import ContinentsTabReport

from gustos.models import winery, award_wine_entity


class GlobalGlobalParticipantsMedalsAndAwardedWines(CoefficientReport, ContinentsTabReport):
    @property
    def title(self):
        return "3.1 Global S & S: Global participants, Medals and Awarded wines"

    @property
    def weight(self):
        return 20

    def get_query(self):
        return self.build_query_for_count_wineries_medals_wines_by_continent(
            event_year=(self.year_from, self.year_to),
            select_fields=(
                func.count(distinct(winery.c.id)).label("WINE PRODUCERS"),
                func.count(distinct(award_wine_entity.c.wine_entity_id)).label("MEDAL WINES"),
                func.count(award_wine_entity.c.award_id).label("MEDALS"),
                (func.count(distinct(award_wine_entity.c.wine_entity_id)) * literal(self.coefficient)).label("POSSIBLE MEDAL WINES"),
                (func.count(award_wine_entity.c.award_id) * literal(self.coefficient)).label("POSSIBLE MEDALS"),
                func.round(func.count(award_wine_entity.c.award_id) / func.count(distinct(award_wine_entity.c.wine_entity_id)), 1).label("AVERAGE MEDALS PER WINE"),
                self.build_continent_case(winery.c.country).label(self.continent_column_name),
            )
        )
