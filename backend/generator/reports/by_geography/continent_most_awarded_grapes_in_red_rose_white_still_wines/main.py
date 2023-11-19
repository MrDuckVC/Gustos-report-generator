import pandas as pd
from sqlalchemy import text

from generator.reports.continent_report import ContinentReport


class ContinentMostAwardedGrapesInRedRoseWhiteStillWinesReport(ContinentReport):
    @property
    def title(self):
        return "4.5 <Continent>: Most awarded grapes in Red / Rose / White Still Wines"

    @property
    def weight(self):
        return 280

    def render(self):
        colors = {
            "Red": self.RED_WINE_WHERE_CLAUSE,
            "White": self.WHITE_WINE_WHERE_CLAUSE,
            "Rose": self.ROSE_WINE_WHERE_CLAUSE,
        }
        grape_mixes = {
            "Blends": self.BLENDS_WINE_HAVING_CLAUSE,
            "Single Variety Wines": self.SINGLE_GRAPE_WINE_HAVING_CLAUSE,
        }

        result = ""
        for color in colors:
            color_result = ""
            for grape in grape_mixes:
                with self.database.connect() as connection:
                    res = connection.execute(
                        text(
                            "SELECT taxonomy_term.name, COUNT(award_wine_entity.award_id) AS MEDALS, COUNT(DISTINCT award_wine_entity.wine_entity_id) AS AWARDED_WINE FROM award_wine_entity "
                            "INNER JOIN award ON award.id = award_wine_entity.award_id "
                            "INNER JOIN event ON event.id = award.event_id "
                            "INNER JOIN wine_entity ON wine_entity.id = award_wine_entity.wine_entity_id "
                            "LEFT JOIN wine_grapes ON wine_grapes.wine_entity = wine_entity.id "
                            "INNER JOIN taxonomy_term ON taxonomy_term.tid = wine_grapes.grape "
                            f"WHERE (event.year BETWEEN {self.year_from} AND {self.year_to}) AND EXISTS( "
                            "SELECT * FROM wine "
                            f"WHERE wine.id = wine_entity.wine AND JSON_UNQUOTE(JSON_EXTRACT(wine.category, '$.\"beverageType\"')) IN (1425) AND {self.STILL_WINE_WHERE_CLAUSE} AND {colors[color]} AND wine.country IN ({', '.join([str(continent) for continent in self.CONTINENTS[self.continent]])})) AND EXISTS( "
                            "SELECT * FROM wine_grapes "
                            "WHERE wine_grapes.wine_entity = wine_entity.id "
                            "GROUP BY wine_grapes.wine_entity "
                            f"HAVING {grape_mixes[grape]}) "
                            "GROUP BY wine_grapes.grape "
                            "ORDER BY AWARDED_WINE DESC "
                            "LIMIT 10")
                    )
                df = pd.DataFrame(res.fetchall(), columns=["GRAPE", "MEDALS", "AWARDED_WINE"])
                color_result = f"{color_result}<p>{grape}</p>{df.to_html()}"

            result = f"{result}<br><div><b>{color} Still Wines</b><div>{color_result}</div></div>"

        return result
