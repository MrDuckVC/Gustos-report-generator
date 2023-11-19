from sqlalchemy import Select, case, select
from sqlalchemy.sql.functions import func

from generator.reports.continents_value_report import ContinentsValueReport
from generator.utils.database import apply_range_filter
from generator.utils.formatting import format_percent
from gustos.models import wine, wine_gwmr, wine_entity


class GlobalIconicWinesDistribution(ContinentsValueReport):

    @property
    def title(self) -> str:
        return "3.1 Global S & S: Global “Iconic wines” wines distribution"

    def format_value(self, value: float | None) -> float | None:
        return format_percent(value)

    def get_query(self) -> Select:
        we = wine_entity.alias("we")
        w = wine.alias("w")

        return apply_range_filter(
            self.build_query_for_wine_entity(
                select_fields=(
                    (func.count(case((wine_gwmr.c.rating > 90, 1))) / func.count() * 100).label(self.value_column_name),
                    self.build_continent_case(w.c.country).label(self.continent_column_name),
                ),
                we=we,
                w=w,
            ) \
                .join(wine_gwmr, wine_gwmr.c.wine_entity_id == we.c.id),
            (wine_gwmr.c.year_from, wine_gwmr.c.year_to),
            (self.year_from, self.year_to),
        ).group_by(self.build_continent_case(w.c.country))

    @property
    def weight(self) -> int:
        return 30