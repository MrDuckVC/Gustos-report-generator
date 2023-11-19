from typing import Any, Dict

from sqlalchemy import Select

from generator.enum import Continent
from generator.reports.histogram_report import HistogramReport


class AverageRatingForWorldRegions(HistogramReport):
    @property
    def title(self) -> str:
        return "3.1 Global S & S: Average rating for World Regions"

    @property
    def weight(self) -> int:
        return 100

    @property
    def get_query_args(self) -> Dict[Any, str]:
        result = {}
        for continent in Continent:
            result[continent.value] = continent.name

        return result

    def get_query(self, argument) -> Select:
        return self.build_query_by_wine_entity(
            countries=self.CONTINENTS[argument],
        )
