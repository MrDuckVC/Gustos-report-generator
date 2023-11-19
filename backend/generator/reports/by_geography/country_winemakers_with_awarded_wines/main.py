import pandas as pd
from sqlalchemy import text

from generator.reports.country_report import CountryReport


class CountryWinemakersWithAwardedWinesReport(CountryReport):
    @property
    def title(self):
        return "4.5 <Country>: Winemakers with awarded wines"

    @property
    def weight(self):
        return 340

    def render(self):
        with self.database.connect() as connection:
            res = connection.execute(
                text(
                    "SELECT taxonomy_term.name AS REGION_NAME, COUNT(DISTINCT winery.id) AS VINEYARD_COUNT FROM award_wine_entity "
                    "INNER JOIN wine_entity ON wine_entity.id = award_wine_entity.wine_entity_id "
                    "INNER JOIN wine_gwmr ON wine_gwmr.wine_entity_id = wine_entity.id "
                    "INNER JOIN wine ON wine.id = wine_entity.wine "
                    "INNER JOIN winery ON winery.id = wine.winery "
                    "INNER JOIN taxonomy_term ON taxonomy_term.tid = wine_entity.region "
                    f"WHERE wine_gwmr.year_from = {self.year_from} AND wine_gwmr.year_to = {self.year_to} AND JSON_UNQUOTE(JSON_EXTRACT(wine.category, '$.\"beverageType\"')) IN (1425) AND wine.country IN ({self.country}) "
                    "GROUP BY taxonomy_term.tid "
                    "ORDER BY VINEYARD_COUNT DESC",
                )
            )

        df = pd.DataFrame(res.fetchall(), columns=["REGION_NAME", "VINEYARD_COUNT"])
        return df.to_html()
