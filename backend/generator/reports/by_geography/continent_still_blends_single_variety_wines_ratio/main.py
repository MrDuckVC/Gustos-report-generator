import base64
from io import BytesIO

import pandas as pd
from sqlalchemy import text

from generator.reports.continent_report import ContinentReport


class ContinentStillBlendsSingleVarietyWinesRatioReport(ContinentReport):
    @property
    def title(self):
        return "4.5 <Continent>: Still Blends / Single variety wines ratio"

    @property
    def weight(self):
        return 110

    def render(self):
        composition_having_case = {
            "BLENDS": self.BLENDS_WINE_HAVING_CLAUSE,
            "SINGLE_VARIETY": self.SINGLE_GRAPE_WINE_HAVING_CLAUSE,
        }

        wine_ratio_category = {
            "WINES": "COUNT(DISTINCT award_wine_entity.wine_entity_id)",
            "MEDALS": "COUNT(award_wine_entity.award_id)",
        }
        page_info = []

        for cat in wine_ratio_category:
            result = {
                "name": cat,
            }
            df_by_composition = pd.DataFrame()
            for composition in composition_having_case:
                with self.database.connect() as connection:
                    res = connection.execute(
                        text(f"SELECT {wine_ratio_category[cat]} AS '' FROM award_wine_entity "
                             "INNER JOIN award ON award.id = award_wine_entity.award_id "
                             "INNER JOIN event ON event.id = award.event_id "
                             "INNER JOIN wine_entity ON wine_entity.id = award_wine_entity.wine_entity_id "
                             "INNER JOIN wine_grapes ON wine_grapes.wine_entity = wine_entity.id "
                             f"WHERE (event.year BETWEEN {self.year_from} AND {self.year_to}) AND EXISTS( "
                             "SELECT * FROM wine "
                             f"WHERE wine.id = wine_entity.wine AND JSON_UNQUOTE(JSON_EXTRACT(wine.category, '$.\"beverageType\"')) IN (1425) AND {self.STILL_WINE_WHERE_CLAUSE} AND wine.country IN ({', '.join([str(continent) for continent in self.CONTINENTS[self.continent]])})) AND EXISTS( "
                             "SELECT * FROM wine_grapes "
                             "WHERE wine_grapes.wine_entity = wine_entity.id "
                             "GROUP BY wine_grapes.wine_entity "
                             f"HAVING {composition_having_case[composition]})",
                             ))
                df = pd.DataFrame(res.fetchall(), columns=[""], dtype=int, index=[composition])
                df_by_composition = pd.concat([df_by_composition, df])

            buffer = BytesIO()
            self.pie_plot(buffer, df_by_composition, figsize=(11, 5))
            result["image"] = f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode('utf-8')}"

            page_info.append(result)

        return self.render_template("wines_pie_ratio.html", page_info=page_info)
