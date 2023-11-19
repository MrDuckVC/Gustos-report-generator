import pandas as pd
from sqlalchemy import text

from generator.reports.country_report import CountryReport


class CountryStillRedRoseWhiteBlendsTopWineriesByAwardedWineReport(CountryReport):
    @property
    def title(self):
        return "4.5 <Country>: Still Red / Rose / White Blends: Top Wineries by Awarded wines"

    @property
    def weight(self):
        return 458

    def render(self):
        colors_ids = {
            "Red": self.RED_WINE_WHERE_CLAUSE,
            "White": self.WHITE_WINE_WHERE_CLAUSE,
            "Rose": self.ROSE_WINE_WHERE_CLAUSE,
        }

        result = ""
        for color in colors_ids:
            with self.database.connect() as connection:
                res = connection.execute(
                    text(
                        "SELECT winery.name AS WINERY_NAME, COUNT(wine_entity.id) AS AWARDED_WINES FROM winery "
                        "INNER JOIN wine ON wine.winery = winery.id "
                        "INNER JOIN wine_entity ON wine_entity.wine = wine.id "
                        "INNER JOIN wine_gwmr ON wine_gwmr.wine_entity_id = wine_entity.id "
                        f"WHERE wine_gwmr.year_from = {self.year_from} AND wine_gwmr.year_to = {self.year_to} AND JSON_UNQUOTE(JSON_EXTRACT(wine.category, '$.\"beverageType\"')) IN (1425) AND {colors_ids[color]} AND winery.country IN ({self.country}) AND {self.STILL_WINE_WHERE_CLAUSE} AND EXISTS( "
                        "SELECT * FROM wine_grapes "
                        "WHERE wine_grapes.wine_entity = wine_entity.id "
                        "GROUP BY wine_grapes.wine_entity "
                        f"HAVING {self.BLENDS_WINE_HAVING_CLAUSE}) "
                        "GROUP BY winery.id "
                        "ORDER BY AWARDED_WINES DESC "
                        "LIMIT 5",
                    )
                )
            df = pd.DataFrame(res.fetchall(), columns=["WINERY_NAME", "AWARDED_WINES"])
            result = f"{result}<b>{color} Wines</b>{df.to_html()}<br>"

        return result
