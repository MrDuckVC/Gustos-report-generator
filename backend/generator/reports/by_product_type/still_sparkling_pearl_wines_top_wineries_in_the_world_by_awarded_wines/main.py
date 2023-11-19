import pandas as pd
from sqlalchemy import text

from generator.reports.report import Report


class StillSparklingPearlWinesTopWineriesInTheWorldByAwardedWines(Report):
    @property
    def title(self):
        return "4.1 Still / Sparkling & Pearl Wines: Top Wineries in the World by Awarded wines"

    @property
    def weight(self):
        return 70

    def render(self):
        product_type_ids = {
            "Still Wines": self.STILL_WINE_WHERE_CLAUSE,
            "Sparkling & Pearl Wines": self.SPARKLING_PEARL_WINE_WHERE_CLAUSE
        }

        result = ""
        for product_type in product_type_ids:
            with self.database.connect() as connection:
                res = connection.execute(
                    text(
                        "SELECT winery.name AS WINERY_NAME, taxonomy_term.name AS COUNTRY, COUNT(wine_entity.id) AS AWARDED_WINES FROM winery "
                        "INNER JOIN taxonomy_term ON taxonomy_term.tid = winery.country "
                        "INNER JOIN wine ON wine.winery = winery.id "
                        "INNER JOIN wine_entity ON wine_entity.wine = wine.id "
                        "INNER JOIN wine_gwmr ON wine_gwmr.wine_entity_id = wine_entity.id "
                        f"WHERE wine_gwmr.year_from = {self.year_from} AND wine_gwmr.year_to = {self.year_to} AND JSON_UNQUOTE(JSON_EXTRACT(wine.category, '$.\"beverageType\"')) IN (1425) AND {product_type_ids[product_type]} "
                        "GROUP BY winery.id "
                        "ORDER BY AWARDED_WINES DESC "
                        "LIMIT 5",
                    )
                )
            df = pd.DataFrame(res.fetchall(),
                              columns=["WINERY_NAME", "COUNTRY", "AWARDED_WINES"])
            result = f"{result}<b>{product_type}</b>{df.to_html()}<br>"

        return result
