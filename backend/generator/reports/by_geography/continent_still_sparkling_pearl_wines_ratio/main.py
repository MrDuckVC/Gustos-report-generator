import base64
from io import BytesIO

import pandas as pd
from sqlalchemy import text

from generator.reports.continent_report import ContinentReport


class ContinentStillSparklingPearlWinesRatioReport(ContinentReport):
    @property
    def title(self):
        return "4.5 <Continent>: Still / Sparkling & Pearl wines ratio"

    @property
    def weight(self):
        return 70

    def render(self):
        wine_ratio_category = {
            "WINES": "COUNT(DISTINCT award_wine_entity.wine_entity_id)",
            "MEDALS": "COUNT(award_wine_entity.award_id)",
        }
        page_info = []

        for cat in wine_ratio_category:
            result = {
                "name": cat,
            }

            with self.database.connect() as connection:
                res = connection.execute(
                    text(
                        f"SELECT {wine_ratio_category[cat]} AS '', (CASE WHEN {self.SPARKLING_PEARL_WINE_WHERE_CLAUSE} THEN 'Sparkling wines\\\\Pearl wines' WHEN {self.STILL_WINE_WHERE_CLAUSE} THEN 'Still wines' END) AS WINE_PRODUCT_TYPE FROM award_wine_entity "
                        "INNER JOIN award ON award.id = award_wine_entity.award_id "
                        "INNER JOIN event ON event.id = award.event_id "
                        "INNER JOIN wine_entity ON wine_entity.id = award_wine_entity.wine_entity_id "
                        "INNER JOIN wine ON wine.id = wine_entity.wine "
                        f"WHERE (event.year BETWEEN {self.year_from} AND {self.year_to}) AND JSON_UNQUOTE(JSON_EXTRACT(wine.category, '$.\"beverageType\"')) IN (1425) AND JSON_UNQUOTE(JSON_EXTRACT(wine.category, '$.\"co2\"')) IN ({self.STILL_WINE_ID}, {', '.join(self.SPARKLING_PEARL_WINE_IDS)}) AND wine.country IN ({', '.join([str(continent) for continent in self.CONTINENTS[self.continent]])}) "
                        "GROUP BY WINE_PRODUCT_TYPE", )
                )

            df = pd.DataFrame(res.fetchall(), columns=["", "WINE_PRODUCT_TYPE"])

            df = df.set_index("WINE_PRODUCT_TYPE")

            buffer = BytesIO()
            self.pie_plot(buffer, df, figsize=(11, 5))
            result["image"] = f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode('utf-8')}"

            page_info.append(result)

        return self.render_template("wines_pie_ratio.html", page_info=page_info)
