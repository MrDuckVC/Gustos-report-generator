from sqlalchemy import Select

from generator.reports.top_wineries_report import TopWineriesReport


class TopWineriesInTheWorldByMedalCount(TopWineriesReport):
    @property
    def value_name(self) -> str:
        return "Medals"

    def get_query(self) -> Select:
        return self.build_query_for_top_wineries_by_medal_count(
            event_year=(self.year_from, self.year_to),
        )

    @property
    def title(self) -> str:
        return "3.1 Global S & S: Top Wineries in the World by Medal Count"


    @property
    def weight(self) -> int:
        return 80