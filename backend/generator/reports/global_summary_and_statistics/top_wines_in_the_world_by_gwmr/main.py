from generator.enum import GWMRUrlRatingType
from generator.reports.top_wines_report import TopWinesReport


class TopWinesInTheWorldByGwmr(TopWinesReport):
    def get_url(self) -> str:
        return self.build_top_wines_url(
            event_year=(self.year_from, self.year_to),
            rating_type=GWMRUrlRatingType.BY_GWMR,
        )

    @property
    def title(self) -> str:
        return "3.1 Global S & S: Top wines in the world by GWMR"


    @property
    def weight(self) -> int:
        return 60
