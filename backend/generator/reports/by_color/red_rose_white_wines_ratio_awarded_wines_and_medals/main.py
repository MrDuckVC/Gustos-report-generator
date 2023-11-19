import base64
from io import BytesIO

import pandas as pd
from sqlalchemy import text

from generator.reports.report import Report


class RedRoseWhiteWinesRatioAwardedWinesAndMedals(Report):
    @property
    def title(self):
        return "4.2 Red / Rose / White wines ratio: Awarded wines and Medal"

    @property
    def weight(self):
        return 10

    def render(self):
        wine_ratio_category = {
            "WINES": "COUNT(DISTINCT award_wine_entity.wine_entity_id)",
            "MEDALS": "COUNT(award_wine_entity.award_id)",
        }
        page_info = []

        for cat in wine_ratio_category:
            result = {"name": cat}

            with self.database.connect() as connection:
                res = connection.execute(
                    text(f"SELECT {wine_ratio_category[cat]} AS '', (CASE WHEN {self.RED_WINE_WHERE_CLAUSE} THEN 'Red' WHEN {self.WHITE_WINE_WHERE_CLAUSE} THEN 'White' WHEN {self.ROSE_WINE_WHERE_CLAUSE} THEN 'Rose' END) AS WINE_COLOR FROM award_wine_entity "
                "INNER JOIN award ON award.id = award_wine_entity.award_id "
                "INNER JOIN event ON event.id = award.event_id "
                "INNER JOIN wine_entity ON wine_entity.id = award_wine_entity.wine_entity_id "
                "INNER JOIN wine ON wine.id = wine_entity.wine "
                f"WHERE (event.year BETWEEN {self.year_from} AND {self.year_to}) AND JSON_UNQUOTE(JSON_EXTRACT(wine.category, '$.\"color\"')) IN ({self.RED_WINE_ID}, {self.WHITE_WINE_ID}, {self.ROSE_WINE_ID}) AND JSON_UNQUOTE(JSON_EXTRACT(wine.category, '$.\"beverageType\"')) IN (1425) "
                "GROUP BY WINE_COLOR")
            )

            df = pd.DataFrame(res.fetchall(), columns=["", "WINE_COLOR"])

            df = df.set_index("WINE_COLOR")
            buffer = BytesIO()
            self.pie_plot(buffer, df, (11, 5))
            result["image"] = f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode('utf-8')}"

            page_info.append(result)

        return self.render_template("wines_pie_ratio.html", page_info=page_info)

