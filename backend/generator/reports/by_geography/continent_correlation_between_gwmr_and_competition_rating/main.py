from sqlalchemy import Select

from generator.reports.continent_report import ContinentReport
from generator.reports.correlation_report import CorrelationReport


class ContinentCorrelationBetweenGwmrAndCompetitionRatingReport(ContinentReport, CorrelationReport):
    @property
    def title(self) -> str:
        return "4.5 <Continent>: Correlation between GWMR and Competition rating"

    @property
    def weight(self) -> int:
        return 50

    @property
    def x_column_name(self) -> str:
        return "COMPETITION RATING"

    @property
    def y_column_name(self) -> str:
        return "GWMR"

    def get_query(self) -> Select:
        return self.build_query_for_correlation_between_gwmr_and_competition_rating(
            event_year=(self.year_from, self.year_to),
            countries_ids=self.CONTINENTS[self.continent],
        )
