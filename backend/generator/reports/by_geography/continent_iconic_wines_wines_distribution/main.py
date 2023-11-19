import pandas as pd
from sqlalchemy import text

from generator.reports.continent_report import ContinentReport


class ContinentIconicWinesWinesDistributionReport(ContinentReport):
    @property
    def title(self):
        return "4.5 <Continent>: “Iconic wines” wines distribution"

    @property
    def weight(self):
        return 30

    def render(self):
        with self.database.connect() as connection:
            res = connection.execute(
                text(
                    f"SELECT COUNT(CASE WHEN {self.ICONIC_WINES_WHERE_CLAUSE} THEN 1 END) AS WITH_HIGH_GWMR_SCORE, COUNT(wine_gwmr.rating) AS WITH_ALL_GWMR_SCORE, taxonomy_term.name AS COUNTRY FROM award_wine_entity "
                    "INNER JOIN wine_entity ON wine_entity.id = award_wine_entity.wine_entity_id "
                    "INNER JOIN wine ON wine.id = wine_entity.wine "
                    "INNER JOIN wine_gwmr ON wine_gwmr.wine_entity_id = wine_entity.id "
                    "INNER JOIN taxonomy_term ON taxonomy_term.tid = wine.country "
                    f"WHERE wine_gwmr.year_from = {self.year_from} AND wine_gwmr.year_to = {self.year_to} AND wine.country IN ({', '.join([str(continent) for continent in self.CONTINENTS[self.continent]])}) AND JSON_UNQUOTE(JSON_EXTRACT(wine.category, '$.\"beverageType\"')) IN (1425) "
                    "GROUP BY wine.country "
                    "ORDER BY WITH_HIGH_GWMR_SCORE DESC",
                    ))

        df = pd.DataFrame(res.fetchall(), columns=["WITH_HIGH_GWMR_SCORE", "WITH_ALL_GWMR_SCORE", "COUNTRY"])

        return f"{df.to_html()}<b>Others are files with zeros</b>"
