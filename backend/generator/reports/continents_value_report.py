from abc import abstractmethod

from django.http import HttpRequest
from sqlalchemy import Select

from generator.reports.report import Report
from generator.enum import Continent


class ContinentsValueReport(Report):
    def __init__(self, request: HttpRequest):
        super().__init__(request)

        self.north_america_value: str | None = None
        """Value of North America continent"""
        self.south_america_value: str | None = None
        """Value of South America continent"""
        self.europe_value: str | None = None
        """Value of Europe continent"""
        self.asia_value: str | None = None
        """Value of Asia continent"""
        self.africa_value: str | None = None
        """Value of Africa continent"""
        self.pacific_value: str | None = None
        """Value of Pacific continent"""

    @property
    def value_column_name(self) -> str:
        """
        :return: Name of column with value.
        """
        return "VALUE"

    @property
    def continent_column_name(self) -> str:
        """
        :return: Name of column with continent.
        """
        return "CONTINENT"

    @abstractmethod
    def get_query(self) -> Select:
        """
        :return: SQLAlchemy query object.
        """
        pass

    def format_value(self, value: str | None) -> str | None:
        """
        :param value: Value to format.

        :return: Formatted value.
        """

        return value

    def render(self):
        query = self.get_query()

        with self.database.connect() as connection:
            result = connection.execute(query).mappings()
            for row in result:
                try:
                    setattr(self, f"{Continent(int(row[self.continent_column_name])).name.lower()}_value", self.format_value(row[self.value_column_name]))
                except ValueError:
                    pass

        return self.render_template(
            "continents_value_report.html",
            **self.to_template_kwargs(),
        )

    def to_template_kwargs(self) -> dict:
        """
        :return: Dictionary which will be passed as keyword arguments to the render_template function.
        """

        return {
            "north_america_value": self.north_america_value,
            "south_america_value": self.south_america_value,
            "europe_value": self.europe_value,
            "asia_value": self.asia_value,
            "africa_value": self.africa_value,
            "pacific_value": self.pacific_value,
        }

