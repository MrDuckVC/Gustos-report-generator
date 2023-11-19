import pandas as pd
from sqlalchemy import text

from generator.reports.continent_report import ContinentReport


class ContinentSparklingPearlWinesTopWineriesByAwardedWineReport(ContinentReport):
    @property
    def title(self):
        return "4.5 <Continent>: Sparkling & Pearl Wines: Top Wineries by Awarded wines"

    @property
    def weight(self):
        return 260

    def render(self):
        with self.database.connect() as connection:
            res = connection.execute(
                text(
                    "SELECT winery.name AS WINERY_NAME, COUNT(wine_entity.id) AS AWARDED_WINES FROM winery "
                    "INNER JOIN wine ON wine.winery = winery.id "
                    "INNER JOIN wine_entity ON wine_entity.wine = wine.id "
                    "INNER JOIN wine_gwmr ON wine_gwmr.wine_entity_id = wine_entity.id "
                    f"WHERE wine_gwmr.year_from = {self.year_from} AND wine_gwmr.year_to = {self.year_to} AND JSON_UNQUOTE(JSON_EXTRACT(wine.category, '$.\"beverageType\"')) IN (1425) AND {self.SPARKLING_PEARL_WINE_WHERE_CLAUSE} and winery.country IN ({', '.join([str(continent) for continent in self.CONTINENTS[self.continent]])}) "
                    "GROUP BY winery.id "
                    "ORDER BY AWARDED_WINES DESC "
                    "LIMIT 5",
                )
            )
        df = pd.DataFrame(res.fetchall(), columns=["WINERY_NAME", "AWARDED_WINES"])

        return df.to_html()
