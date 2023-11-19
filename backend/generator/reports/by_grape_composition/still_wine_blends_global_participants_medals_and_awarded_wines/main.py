import pandas as pd
from sqlalchemy import text

from generator.enum import Continent
from generator.reports.report import Report


class StillWineBlendsGlobalParticipantsMedalsAndAwardedWines(Report):
    @property
    def title(self):
        return "4.3 Still wine Blends: Global participants, Medals and Awarded wines"

    @property
    def weight(self):
        return 30

    def render(self):
        data = {}
        for continent in self.CONTINENTS:
            with self.database.connect() as connection:
                res = connection.execute(
                    text(
                        "SELECT COUNT(DISTINCT wine.winery) AS MANUFACTURES, COUNT(DISTINCT award_wine_entity.wine_entity_id) AS 'MEDAL WINES', COUNT(award_wine_entity.award_id) AS MEDALS FROM award_wine_entity "
                        "INNER JOIN award ON award.id = award_wine_entity.award_id "
                        "INNER JOIN event ON event.id = award.event_id "
                        "INNER JOIN wine_entity ON wine_entity.id = award_wine_entity.wine_entity_id "
                        "INNER JOIN wine ON wine.id = wine_entity.wine "
                        "INNER JOIN wine_grapes ON wine_grapes.wine_entity = wine_entity.id "
                        f"WHERE (event.year BETWEEN {self.year_from} AND {self.year_to}) AND EXISTS ( "
                        "SELECT * FROM winery "
                        f"WHERE winery.id = wine.winery AND winery.country IN ({', '.join([str(continent) for continent in self.CONTINENTS[continent]])})) AND {self.STILL_WINE_WHERE_CLAUSE} AND JSON_UNQUOTE(JSON_EXTRACT(wine.category, '$.\"beverageType\"')) in (1425) AND EXISTS( "
                        "SELECT * FROM wine_grapes "
                        "WHERE wine_grapes.wine_entity = wine_entity.id "
                        "GROUP BY wine_grapes.wine_entity "
                        f"HAVING {self.BLENDS_WINE_HAVING_CLAUSE})",
                        ))
            data[continent] = res.fetchall()[0]
        df = pd.DataFrame(data, index=["MANUFACTURES", "MEDAL WINES", "MEDALS"]).transpose()
        africa_tab_name = None
        africa_data = [
            {
                "name": "MANUFACTURES",
                "value": df.loc[Continent.AFRICA.value]["MANUFACTURES"],
            },
            {
                "name": "MEDAL WINES",
                "value": df.loc[Continent.AFRICA.value]["MEDAL WINES"],
            },
            {
                "name": "MEDALS",
                "value": df.loc[Continent.AFRICA.value]["MEDALS"],
            },
        ]

        asia_tab_name = None
        asia_data = [
            {
                "name": "MANUFACTURES",
                "value": df.loc[Continent.ASIA.value]["MANUFACTURES"],
            },
            {
                "name": "MEDAL WINES",
                "value": df.loc[Continent.ASIA.value]["MEDAL WINES"],
            },
            {
                "name": "MEDALS",
                "value": df.loc[Continent.ASIA.value]["MEDALS"],
            },
        ]

        europe_tab_name = None
        europe_data = [
            {
                "name": "MANUFACTURES",
                "value": df.loc[Continent.EUROPE.value]["MANUFACTURES"],
            },
            {
                "name": "MEDAL WINES",
                "value": df.loc[Continent.EUROPE.value]["MEDAL WINES"],
            },
            {
                "name": "MEDALS",
                "value": df.loc[Continent.EUROPE.value]["MEDALS"],
            },
        ]

        north_america_tab_name = None
        north_america_data = [
            {
                "name": "MANUFACTURES",
                "value": df.loc[Continent.NORTH_AMERICA.value]["MANUFACTURES"],
            },
            {
                "name": "MEDAL WINES",
                "value": df.loc[Continent.NORTH_AMERICA.value]["MEDAL WINES"],
            },
            {
                "name": "MEDALS",
                "value": df.loc[Continent.NORTH_AMERICA.value]["MEDALS"],
            },
        ]

        pacific_tab_name = None
        pacific_data = [
            {
                "name": "MANUFACTURES",
                "value": df.loc[Continent.PACIFIC.value]["MANUFACTURES"],
            },
            {
                "name": "MEDAL WINES",
                "value": df.loc[Continent.PACIFIC.value]["MEDAL WINES"],
            },
            {
                "name": "MEDALS",
                "value": df.loc[Continent.PACIFIC.value]["MEDALS"],
            },
        ]

        south_america_tab_name = None
        south_america_data = [
            {
                "name": "MANUFACTURES",
                "value": df.loc[Continent.SOUTH_AMERICA.value]["MANUFACTURES"],
            },
            {
                "name": "MEDAL WINES",
                "value": df.loc[Continent.SOUTH_AMERICA.value]["MEDAL WINES"],
            },
            {
                "name": "MEDALS",
                "value": df.loc[Continent.SOUTH_AMERICA.value]["MEDALS"],
            },
        ]

        return self.render_template(
            "continents_tab_report.html",
            africa_tab_name=africa_tab_name,
            africa_data=africa_data,
            asia_tab_name=asia_tab_name,
            asia_data=asia_data,
            europe_tab_name=europe_tab_name,
            europe_data=europe_data,
            pacific_tab_name=pacific_tab_name,
            pacific_data=pacific_data,
            north_america_tab_name=north_america_tab_name,
            north_america_data=north_america_data,
            south_america_tab_name=south_america_tab_name,
            south_america_data=south_america_data,
        )
