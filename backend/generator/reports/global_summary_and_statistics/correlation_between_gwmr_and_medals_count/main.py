from sqlalchemy import Select

from generator.reports.correlation_report import CorrelationReport


class CorrelationBetweenGwmrAndMedalsCount(CorrelationReport):

    @property
    def x_column_name(self) -> str:
        return "MEDALS COUNT"

    @property
    def y_column_name(self) -> str:
        return "GWMR"

    def get_query(self) -> Select:
        return self.build_query_for_correlation_between_gwmr_and_medal_count(
            event_year=(self.year_from, self.year_to),
        )

    @property
    def title(self) -> str:
        return "3.1 Global S & S: Correlation between GWMR and Medals Count"

    @property
    def weight(self) -> int:
        return 50
