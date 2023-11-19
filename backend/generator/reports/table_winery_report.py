from abc import abstractmethod
from enum import Enum
from typing import Any, Sequence

from django.http import HttpRequest
from sqlalchemy import CursorResult, select

from generator.exceptions import DataNotFoundException
from generator.enum import Continent
from generator.reports.winery_report import WineryReport
from generator.utils.formatting import format_continent_name

from gustos.models import taxonomy_term, winery


class _RatingType(Enum):
    ALL = None
    WORLD = "world"
    CONTINENT = "continent"
    COUNTRY = "country"


class _RowType(Enum):
    PREVIOUS = "previous"
    CURRENT = "current"
    NEXT = "next"


class TableWineryReport(WineryReport):

    @property
    @abstractmethod
    def parameter_title(self):
        pass

    @abstractmethod
    def get_query(self):
        pass

    @abstractmethod
    def format_entity_name(self, name):
        pass

    @abstractmethod
    def format_entity_value(self, value):
        pass

    @abstractmethod
    def get_template_kwargs(self):
        pass

    def __init__(self, request: HttpRequest):
        super().__init__(request)

        self.continent_id = None
        """The machine name of the continent of the searched (current) entity."""
        self.continent_name = None
        """The human-readable name of the continent of the searched (current) entity."""
        self.country_id = None
        """The identifier of the country of the searched (current) entity."""
        self.country_name = None
        """The human-readable name of the country of the searched (current) entity."""

        self.current_row = None
        """The full row from query result of the searched (current) entity."""

        self.world_previous_row_rank = None
        """The rank of the entity which precedes the searched (current) entity in the world ranking."""
        self.world_previous_row_name = None
        """The name of the entity which precedes the searched (current) entity in the world ranking."""
        self.world_previous_row_value = None
        """The value of the entity which precedes the searched (current) entity in the world ranking."""
        self.world_previous_row = None
        """The full row from query result of entity which precedes the searched (current) entity in the world ranking."""
        self.world_current_row_rank = None
        """The rank of the searched (current) entity in the world ranking."""
        self.world_current_row_name = None
        """The name of the searched (current) entity in the world ranking."""
        self.world_current_row_value = None
        """The value of the searched (current) entity in the world ranking."""
        self.world_next_row_rank = None
        """The rank of the entity which follows the searched (current) entity in the world ranking."""
        self.world_next_row_name = None
        """The name of the entity which follows the searched (current) entity in the world ranking."""
        self.world_next_row_value = None
        """The value of the entity which follows the searched (current) entity in the world ranking."""
        self.world_next_row = None
        """The full row from query result of entity which follows the searched (current) entity in the world ranking."""
        self.world_percent_rank = None
        """The percentage rank of the searched (current) entity in the world ranking."""

        self.continent_previous_row_rank = None
        """The rank of the entity which precedes the searched (current) entity in the continent ranking."""
        self.continent_previous_row_name = None
        """The name of the entity which precedes the searched (current) entity in the continent ranking."""
        self.continent_previous_row_value = None
        """The value of the entity which precedes the searched (current) entity in the continent ranking."""
        self.continent_previous_row = None
        """The full row from query result of entity which precedes the searched (current) entity in the continent ranking."""
        self.continent_current_row_rank = None
        """The rank of the searched (current) entity in the continent ranking."""
        self.continent_current_row_name = None
        """The name of the searched (current) entity in the continent ranking."""
        self.continent_current_row_value = None
        """The value of the searched (current) entity in the continent ranking."""
        self.continent_next_row_rank = None
        """The rank of the entity which follows the searched (current) entity in the continent ranking."""
        self.continent_next_row_name = None
        """The name of the entity which follows the searched (current) entity in the continent ranking."""
        self.continent_next_row_value = None
        """The value of the entity which follows the searched (current) entity in the continent ranking."""
        self.continent_next_row = None
        """The full row from query result of entity which follows the searched (current) entity in the continent ranking."""
        self.continent_percent_rank = None
        """The percentage rank of the searched (current) entity in the continent ranking."""

        self.country_previous_row_rank = None
        """The rank of the entity which precedes the searched (current) entity in the country ranking."""
        self.country_previous_row_name = None
        """The name of the entity which precedes the searched (current) entity in the country ranking."""
        self.country_previous_row_value = None
        """The value of the entity which precedes the searched (current) entity in the country ranking."""
        self.country_previous_row = None
        """The full row from query result of entity which precedes the searched (current) entity in the country ranking."""
        self.country_current_row_rank = None
        """The rank of the searched (current) entity in the country ranking."""
        self.country_current_row_name = None
        """The name of the searched (current) entity in the country ranking."""
        self.country_current_row_value = None
        """The value of the searched (current) entity in the country ranking."""
        self.country_next_row_rank = None
        """The rank of the entity which follows the searched (current) entity in the country ranking."""
        self.country_next_row_name = None
        """The name of the entity which follows the searched (current) entity in the country ranking."""
        self.country_next_row_value = None
        """The value of the entity which follows the searched (current) entity in the country ranking."""
        self.country_next_row = None
        """The full row from query result of entity which follows the searched (current) entity in the country ranking."""
        self.country_percent_rank = None
        """The percentage rank of the searched (current) entity in the country ranking."""

    def fill_continent_and_country(self):
        with self.database.connect() as connection:
            query = select(
                winery.c.country.label('country_id'),
                taxonomy_term.c.name.label('country_name'),
                self.build_continent_case(winery.c.country).label('continent_id'),
            ).select_from(winery) \
                .join(taxonomy_term, winery.c.country == taxonomy_term.c.tid) \
                .where(winery.c.id == self.winery_id)
            self.country_id, self.country_name, self.continent_id = connection.execute(query).fetchone()
            self.continent_name = format_continent_name(self.continent_id)

    def get_ratings_by_query_result(
            self,
            cursor_result: CursorResult,
            world_rank_index: int,
            world_percent_rank_index: int,
            continent_rank_index: int,
            continent_percent_rank_index: int,
            continent_id_index: int,
            continent_id: Continent,
            country_rank_index: int,
            country_percent_rank_index: int,
            country_id_index: int,
            country_id: int,
            entity_name_index: Sequence[int] | int,
            entity_value_index: int,
            entity_id_index: int,
            entity_id: int,
    ):
        """
        Iterates over the query result and return the ratings for the given entity.

        :param cursor_result: The query result.
        :param world_rank_index: The index of the world rank column in query result.
        :param world_percent_rank_index: The index of the world percent rank column in query result.
        :param continent_rank_index: The index of the continent rank column in query result.
        :param continent_percent_rank_index: The index of the continent percent rank column in query result.
        :param continent_id_index: The index of the continent id column in query result.
        :param continent_id: The identifier of the winery continent.
        :param country_rank_index: The index of the country rank column in query result.
        :param country_percent_rank_index: The index of the country percent rank column in query result.
        :param country_id_index: The index of the country id column in query result.
        :param country_id: The identifier of the winery country.
        :param entity_name_index: The index of the entity name column in query result.
        :param entity_value_index: The index of the entity value column in query result.
        :param entity_id_index: The index of the entity id column in query result.
        :param entity_id: The identifier of the entity.
        """

        if isinstance(continent_id, Continent):
            continent_id = continent_id.value

        world_pre_previous_row = cursor_result.fetchone()

        # Cursor result is empty.
        if world_pre_previous_row is None:
            raise DataNotFoundException("No data found.")

        if world_pre_previous_row[continent_id_index] == continent_id:
            continent_pre_previous_row = world_pre_previous_row
        else:
            continent_pre_previous_row = None, None, None
        if world_pre_previous_row[country_id_index] == country_id:
            country_pre_previous_row = world_pre_previous_row
        else:
            country_pre_previous_row = None, None, None

        def get_row_name(row: Sequence[Any]):
            """
            Returns the name of the entity.

            :param row: The row of the query result.
            """
            if isinstance(entity_name_index, Sequence):
                return tuple(row[i] for i in entity_name_index)
            else:
                return row[entity_name_index]

        percent_rank_index_dict = {
            _RatingType.WORLD: world_percent_rank_index,
            _RatingType.CONTINENT: continent_percent_rank_index,
            _RatingType.COUNTRY: country_percent_rank_index,
        }
        rank_index_dict = {
            _RatingType.WORLD: world_rank_index,
            _RatingType.CONTINENT: continent_rank_index,
            _RatingType.COUNTRY: country_rank_index,
        }

        def update_row(rating_type: _RatingType, row_type: _RowType, row: Sequence[Any] | None):
            if rating_type == _RatingType.ALL:
                for rt in [_RatingType.WORLD, _RatingType.CONTINENT, _RatingType.COUNTRY]:
                    update_row(rt, row_type, row)
            elif row is None:
                setattr(self, f"{rating_type.value}_{row_type.value}_row_rank", None)
                setattr(self, f"{rating_type.value}_{row_type.value}_row_name", None)
                setattr(self, f"{rating_type.value}_{row_type.value}_row_value", None)
                setattr(self, f"{rating_type.value}_{row_type.value}_row", None)
                if row_type == _RowType.CURRENT:
                    setattr(self, f"{rating_type.value}_percent_rank", None)
                    self.current_row = None
            else:
                setattr(self, f"{rating_type.value}_{row_type.value}_row_rank", row[rank_index_dict[rating_type]])
                setattr(self, f"{rating_type.value}_{row_type.value}_row_name", get_row_name(row))
                setattr(self, f"{rating_type.value}_{row_type.value}_row_value", row[entity_value_index])
                setattr(self, f"{rating_type.value}_{row_type.value}_row", row)
                if row_type == _RowType.CURRENT:
                    setattr(self, f"{rating_type.value}_percent_rank", row[percent_rank_index_dict[rating_type]])
                    self.current_row = row

        # Check if the first row contains the entity we are looking for.
        if world_pre_previous_row[entity_id_index] == entity_id:
            update_row(_RatingType.ALL, _RowType.CURRENT, world_pre_previous_row)
        else:
            # So if 'world_pre_previous_row' is not current row, it is previous one.
            update_row(_RatingType.WORLD, _RowType.PREVIOUS, world_pre_previous_row)
            if world_pre_previous_row[continent_id_index] == continent_id:
                update_row(_RatingType.CONTINENT, _RowType.PREVIOUS, world_pre_previous_row)
                # Obviously, check country ranking only if continent matches.
                if world_pre_previous_row[country_id_index] == country_id:
                    update_row(_RatingType.COUNTRY, _RowType.PREVIOUS, world_pre_previous_row)

            # Search for the entity in the rest of the rows and memorize the previous row for each separate ranking.
            for row in cursor_result:
                if row[entity_id_index] == entity_id:
                    update_row(_RatingType.ALL, _RowType.CURRENT, row)

                    if self.world_previous_row_rank == row[world_rank_index]:
                        update_row(_RatingType.WORLD, _RowType.PREVIOUS, world_pre_previous_row)

                    if self.continent_previous_row_rank == row[continent_rank_index]:
                        update_row(_RatingType.CONTINENT, _RowType.PREVIOUS, continent_pre_previous_row)

                    if self.country_previous_row_rank == row[country_rank_index]:
                        update_row(_RatingType.COUNTRY, _RowType.PREVIOUS, country_pre_previous_row)

                    break

                if row[world_rank_index] != self.world_previous_row_rank:
                    world_pre_previous_row = self.world_previous_row
                    update_row(_RatingType.WORLD, _RowType.PREVIOUS, row)

                if row[continent_id_index] == continent_id:
                    if row[continent_rank_index] != self.continent_previous_row_rank:
                        continent_pre_previous_row = self.continent_previous_row
                        update_row(_RatingType.CONTINENT, _RowType.PREVIOUS, row)

                    if row[country_id_index] == country_id and row[country_rank_index] != self.country_previous_row_rank:
                        country_pre_previous_row = self.country_previous_row
                        update_row(_RatingType.COUNTRY, _RowType.PREVIOUS, row)

        # Entity does not exist in cursor self.
        if self.world_current_row_rank is None:
            raise DataNotFoundException("No data found.")

        # Search the next row in world ranking and if we're lucky also in continent and country ranking.
        for row in cursor_result:
            if row[world_rank_index] != self.world_current_row_rank:
                update_row(_RatingType.WORLD, _RowType.NEXT, row)

                if row[continent_id_index] == continent_id:
                    if row[continent_rank_index] != self.continent_current_row_rank:
                        update_row(_RatingType.CONTINENT, _RowType.NEXT, row)
                    # Obviously, check country ranking only if continent matches.
                    if row[country_id_index] == country_id and row[country_rank_index] != self.country_current_row_rank:
                        update_row(_RatingType.COUNTRY, _RowType.NEXT, row)
                break

        # Search the next row in continent ranking only if we didn't find it in the previous loop.
        if self.continent_next_row_rank is None:
            # Search the next row in continent ranking and if we're lucky also in country ranking.
            for row in cursor_result:
                if row[continent_id_index] == continent_id:
                    if row[continent_rank_index] != self.continent_current_row_rank:
                        update_row(_RatingType.CONTINENT, _RowType.NEXT, row)
                    # Obviously, check country ranking only if continent matches.
                    if row[country_id_index] == country_id and row[country_rank_index] != self.country_current_row_rank:
                        update_row(_RatingType.COUNTRY, _RowType.NEXT, row)
                    break

        # Search the next row in country ranking only if we didn't find it in the previous loop.
        if self.country_next_row_rank is None:
            # Search the next row in country ranking.
            for row in cursor_result:
                if row[country_id_index] == country_id and row[country_rank_index] != self.country_current_row_rank:
                    update_row(_RatingType.COUNTRY, _RowType.NEXT, row)
                    break

    def to_template_kwargs(self):
        """
        Returns a dictionary which will be passed as keyword arguments to the render_template function.
        """
        return {
            "world_previous_row_rank": self.world_previous_row_rank,
            "world_previous_row_name": self.format_entity_name(self.world_previous_row_name),
            "world_previous_row_value": self.format_entity_value(self.world_previous_row_value),
            "world_current_row_rank": self.world_current_row_rank,
            "world_current_row_name": self.format_entity_name(self.world_current_row_name),
            "world_current_row_value": self.format_entity_value(self.world_current_row_value),
            "world_next_row_rank": self.world_next_row_rank,
            "world_next_row_name": self.format_entity_name(self.world_next_row_name),
            "world_next_row_value": self.format_entity_value(self.world_next_row_value),
            "continent_previous_row_rank": self.continent_previous_row_rank,
            "continent_previous_row_name": self.format_entity_name(self.continent_previous_row_name),
            "continent_previous_row_value": self.format_entity_value(self.continent_previous_row_value),
            "continent_current_row_rank": self.continent_current_row_rank,
            "continent_current_row_name": self.format_entity_name(self.continent_current_row_name),
            "continent_current_row_value": self.format_entity_value(self.continent_current_row_value),
            "continent_next_row_rank": self.continent_next_row_rank,
            "continent_next_row_name": self.format_entity_name(self.continent_next_row_name),
            "continent_next_row_value": self.format_entity_value(self.continent_next_row_value),
            "country_previous_row_rank": self.country_previous_row_rank,
            "country_previous_row_name": self.format_entity_name(self.country_previous_row_name),
            "country_previous_row_value": self.format_entity_value(self.country_previous_row_value),
            "country_current_row_rank": self.country_current_row_rank,
            "country_current_row_name": self.format_entity_name(self.country_current_row_name),
            "country_current_row_value": self.format_entity_value(self.country_current_row_value),
            "country_next_row_rank": self.country_next_row_rank,
            "country_next_row_name": self.format_entity_name(self.country_next_row_name),
            "country_next_row_value": self.format_entity_value(self.country_next_row_value),
            **self.get_template_kwargs(),
        }
