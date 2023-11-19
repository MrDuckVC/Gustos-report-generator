import pandas as pd
from sqlalchemy import text

from generator.reports.country_report import CountryReport


class CountryMostAwardedGrapesInRedRoseWhiteStillWinesReport(CountryReport):
    @property
    def title(self):
        return "4.5 <Country>: Most awarded grapes in Red / Rose / White Still Wines"

    @property
    def weight(self):
        return 470

    def render(self):
        colors = {
            "Red": self.RED_WINE_WHERE_CLAUSE,
            "White": self.WHITE_WINE_WHERE_CLAUSE,
            "Rose": self.ROSE_WINE_WHERE_CLAUSE,
        }
        grape_mix = {
            "Blends": "NOT",
            "Single Variety Wines": "",
        }

        result = ""
        for color in colors:
            color_result = ""
            for grape in grape_mix:
                with self.database.connect() as connection:
                    res = connection.execute(
                        text(
                            "SELECT COUNT(award_wine_entity.award_id) AS MEDALS, COUNT(DISTINCT award_wine_entity.wine_entity_id) AS AWARDED_WINE, taxonomy_term.name AS GRAPE_NAME FROM award_wine_entity "
                            "INNER JOIN award ON award.id = award_wine_entity.award_id "
                            "INNER JOIN event ON event.id = award.event_id "
                            "INNER JOIN wine_entity ON wine_entity.id = award_wine_entity.wine_entity_id "
                            "INNER JOIN wine ON wine.id = wine_entity.wine "
                            "INNER JOIN wine_grapes ON wine_grapes.wine_entity = wine_entity.id "
                            "INNER JOIN taxonomy_term ON taxonomy_term.tid = wine_grapes.grape "
                            f"WHERE (event.year BETWEEN {self.year_from} AND {self.year_to}) AND wine.id = wine_entity.wine AND wine.country IN ({self.country}) AND JSON_UNQUOTE(JSON_EXTRACT(wine.category, '$.\"beverageType\"')) IN (1425) AND {colors[color]} AND {self.STILL_WINE_WHERE_CLAUSE} AND {grape_mix[grape]} EXISTS ( "
                            "SELECT * FROM wine_grapes "
                            f"WHERE wine_grapes.wine_entity = wine_entity.id AND {self.SINGLE_GRAPE_WHERE_EXISTS_CLAUSE}) "
                            "GROUP BY wine_grapes.grape "
                            "ORDER BY AWARDED_WINE DESC "
                            "LIMIT 10",
                            ))

                df = pd.DataFrame(res.fetchall(), columns=["MEDALS", "AWARDED_WINE", "GRAPE_NAME"])
                color_result = f"{color_result}<p>{grape}</p>{df.to_html()}"

            result = f"{result}<br><div><b>{color} Still Wines</b><div>{color_result}</div></div>"

        return result
