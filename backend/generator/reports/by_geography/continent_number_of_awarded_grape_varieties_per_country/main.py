import pandas as pd
from sqlalchemy import text

from generator.reports.continent_report import ContinentReport


class ContinentNumberOfAwardedGrapeVarietiesPerCountryReport(ContinentReport):
    @property
    def title(self):
        return "4.5 <Continent>: Number of awarded grape varieties per country"

    @property
    def weight(self):
        return 270

    def render(self):
        with self.database.connect() as connection:
            res = connection.execute(
                text(
                    "SELECT COUNT(DISTINCT wine_grapes.grape) AS NUMBER_OF_GRAPE, taxonomy_term.name AS GRAPE FROM wine_grapes "
                    "INNER JOIN wine ON wine.id = wine_grapes.wine "
                    "INNER JOIN taxonomy_term ON taxonomy_term.tid = wine.country "
                    f"WHERE JSON_UNQUOTE(JSON_EXTRACT(wine.category, '$.\"beverageType\"')) IN (1425) AND wine.country IN ({', '.join([str(continent) for continent in self.CONTINENTS[self.continent]])}) AND EXISTS( "
                    "SELECT * FROM wine_entity "
                    "INNER JOIN wine_gwmr ON wine_gwmr.wine_entity_id = wine_entity.id "
                    f"WHERE wine_entity.wine = wine.id AND wine_gwmr.year_from = {self.year_from} AND wine_gwmr.year_to = {self.year_to}) "
                    "GROUP BY wine.country "
                    "ORDER BY NUMBER_OF_GRAPE DESC",
                )
            )

        df = pd.DataFrame(res.fetchall(), columns=["NUMBER_OF_GRAPE", "GRAPE"])
        return df.to_html()
