import base64
from io import BytesIO

import pandas as pd
from sqlalchemy import text

from generator.reports.continent_report import ContinentReport


class ContinentAwardCategoryDistributionForBlendSingleVarietyStillWinesReport(ContinentReport):
    @property
    def title(self):
        return "4.5 <Continent>: Award category distribution for Blend / Single variety still wine"

    @property
    def weight(self):
        return 120

    def render(self):
        grape_compositions = {
            "BLEND WINES": self.BLENDS_WINE_HAVING_CLAUSE,
            "SINGLE WINES": self.SINGLE_GRAPE_WINE_HAVING_CLAUSE,
        }

        page_info = []

        for composition in grape_compositions:
            result = {
                "title": composition,
            }
            with self.database.connect() as connection:
                res = connection.execute(
                    text("SELECT award.value AS MEDAL, COUNT(award_wine_entity.wine_entity_id) AS WINE_COUNT FROM award_wine_entity "
                    "INNER JOIN wine_entity ON wine_entity.id = award_wine_entity.wine_entity_id "
                    "INNER JOIN wine ON wine.id = wine_entity.wine "
                    "INNER JOIN award ON award.id = award_wine_entity.award_id "
                    "INNER JOIN event ON event.id = award.event_id "
                    f"WHERE (event.year BETWEEN {self.year_from} AND {self.year_to}) AND JSON_UNQUOTE(JSON_EXTRACT(wine.category, '$.\"beverageType\"')) IN (1425) AND {self.STILL_WINE_WHERE_CLAUSE} AND wine.country IN ({', '.join([str(continent) for continent in self.CONTINENTS[self.continent]])}) AND EXISTS( "
                    "SELECT * FROM wine_grapes "
                    "WHERE wine_grapes.wine_entity = wine_entity.id "
                    "GROUP BY wine_grapes.wine_entity "
                    f"HAVING {grape_compositions[composition]}) "
                    "GROUP BY award.value"),
                )

            df = pd.DataFrame(res.fetchall(), columns=["MEDAL", "WINE_COUNT"], dtype=int).set_index("MEDAL")
            df["WINE_COUNT"] = (df["WINE_COUNT"] / df["WINE_COUNT"].sum()) * 100

            buffer = BytesIO()
            self.bar_plot(buffer, df, figsize=(4, 5))
            result["image"] = f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode('utf-8')}"
            page_info.append(result)

        return self.render_template("bar_diagrams/simple.html", page_info=page_info)
