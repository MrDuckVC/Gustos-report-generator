from sqlalchemy import select, func, case, distinct, literal

from generator.reports.coefficient_report import CoefficientReport
from generator.reports.continents_tab_report import ContinentsTabReport
from generator.enum import CompetitionRegion, BeverageType
from generator.utils.database import apply_range_filter

from gustos.models import (
    competition, wine,
    wine_entity, award_wine_entity,
    award, event,
)


class GlobalCompetitionsAndMedals(CoefficientReport, ContinentsTabReport):
    @property
    def title(self):
        return "3.1 Global S & S: Global Competitions and Medals"

    @property
    def weight(self):
        return 10

    def get_query(self):
        case_list = []
        for region in CompetitionRegion:
            if region.get_continent():
                case_list.append((competition.c.region == region.value, region.get_continent().value))

        m_case = case(
            *case_list,
        )

        return apply_range_filter(
            select(
                m_case.label(self.continent_column_name),
                func.count(distinct(competition.c.id)).label("COMPETITIONS"),
                func.count(award_wine_entity.c.award_id).label("MEDALS"),
                (func.count(award_wine_entity.c.award_id) * literal(self.coefficient)).label("POSSIBLE MEDALS"),
            ).select_from(competition) \
                .join(event, event.c.competition_id == competition.c.id) \
                .join(award, award.c.event_id == event.c.id) \
                .join(award_wine_entity, award_wine_entity.c.award_id == award.c.id) \
                .join(wine_entity, wine_entity.c.id == award_wine_entity.c.wine_entity_id) \
                .join(wine, wine.c.id == wine_entity.c.wine) \
                .where(
                func.json_unquote(func.json_extract(wine.c.category, '$."beverageType"')) == BeverageType.WINE,
                    m_case.is_not(None),
                ) \
                .group_by(self.continent_column_name),
                event.c.year,
                (self.year_from, self.year_to),
        )
