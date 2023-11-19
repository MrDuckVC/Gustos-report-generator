from sqlalchemy import Select

from generator.reports.correlation_report import CorrelationReport
from generator.reports.continent_report import ContinentReport


class ContinentCorrelationBetweenGwmrAndMedalsCountReport(ContinentReport, CorrelationReport):
    @property
    def x_column_name(self) -> str:
        return "MEDALS COUNT"

    @property
    def y_column_name(self) -> str:
        return "GWMR"

    def get_query(self) -> Select:
        return self.build_query_for_correlation_between_gwmr_and_medal_count(
            event_year=(self.year_from, self.year_to),
            countries_ids=self.CONTINENTS[self.continent],
        )

    @property
    def title(self) -> str:
        return "4.5 <Continent>: Correlation between GWMR and Medals Count"

    @property
    def weight(self) -> int:
        return 60
