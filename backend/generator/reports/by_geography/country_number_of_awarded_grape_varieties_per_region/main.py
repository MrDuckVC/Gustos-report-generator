import pandas as pd
from sqlalchemy import text

from generator.reports.country_report import CountryReport


class CountryNumberOfAwardedGrapeVarietiesPerRegionReport(CountryReport):
    @property
    def title(self):
        return "4.5 <Country>: Number of awarded grape varieties per region"

    @property
    def weight(self):
        return 469

    def render(self):
        with self.database.connect() as connection:
            res = connection.execute(
                text(
                    "SELECT COUNT(DISTINCT wine_grapes.grape) AS NUMBER_OF_GRAPE, taxonomy_term.name AS GRAPE FROM wine_grapes "
                    "INNER JOIN wine_entity ON wine_entity.id = wine_grapes.wine_entity "
                    "INNER JOIN taxonomy_term ON taxonomy_term.tid = wine_entity.region "
                    "INNER JOIN wine_gwmr ON wine_gwmr.wine_entity_id = wine_entity.id "
                    f"WHERE wine_gwmr.year_from = {self.year_from} AND wine_gwmr.year_to = {self.year_to} AND EXISTS( "
                    "SELECT * FROM wine "
                    f"WHERE wine.id = wine_entity.wine AND JSON_UNQUOTE(JSON_EXTRACT(wine.category, '$.\"beverageType\"')) IN (1425) AND wine.country IN ({self.country})) "
                    "GROUP BY wine_entity.region "
                    "ORDER BY NUMBER_OF_GRAPE DESC",
                )
            )

        df = pd.DataFrame(res.fetchall(), columns=["NUMBER_OF_GRAPE", "GRAPE"])
        return df.to_html()
