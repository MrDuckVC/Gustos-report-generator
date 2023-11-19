import pandas as pd
from sqlalchemy import text

from generator.reports.country_report import CountryReport


class CountryMostAwardedGrapesInSparklingPearlWinesReport(CountryReport):
    @property
    def title(self):
        return "4.5 <Country>: Most awarded grapes in Sparkling & Pearl Wines"

    @property
    def weight(self):
        return 490

    def render(self):
        colors = {
            "White": self.WHITE_WINE_WHERE_CLAUSE,
            "Rose": self.ROSE_WINE_WHERE_CLAUSE,
        }

        result = ""
        for color in colors:
            with self.database.connect() as connection:
                res = connection.execute(
                    text(
                        "SELECT taxonomy_term.name AS GRAPE, COUNT(award_wine_entity.award_id) AS MEDAL_COUNT FROM award_wine_entity "
                        "INNER JOIN award ON award.id = award_wine_entity.award_id "
                        "INNER JOIN event ON event.id = award.event_id "
                        "INNER JOIN wine_entity ON wine_entity.id = award_wine_entity.wine_entity_id "
                        "INNER JOIN wine_grapes ON wine_grapes.wine_entity = wine_entity.id "
                        "INNER JOIN taxonomy_term ON taxonomy_term.tid = wine_grapes.grape "
                        f"WHERE (event.year BETWEEN {self.year_from} AND {self.year_to}) AND EXISTS( "
                        "SELECT * FROM wine "
                        f"WHERE wine.id = wine_entity.wine AND wine.country IN ({self.country}) AND JSON_UNQUOTE(JSON_EXTRACT(wine.category, '$.\"beverageType\"')) IN (1425) AND {colors[color]} AND {self.SPARKLING_PEARL_WINE_WHERE_CLAUSE}) "
                        "GROUP BY wine_grapes.grape "
                        "ORDER BY MEDAL_COUNT DESC "
                        "LIMIT 10",
                        ))
            df = pd.DataFrame(res.fetchall(), columns=["GRAPE", "MEDAL_COUNT"])
            result = f"{result}<div><p>Sparkling or Pearl {color} Wines</p>{df.to_html()}</div>"

        return result
