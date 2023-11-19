import base64
from io import BytesIO

import pandas as pd
from sqlalchemy import text

from generator.reports.country_report import CountryReport


class CountryAwardCategoryDistributionForRedRoseWhiteWinesReport(CountryReport):
    @property
    def title(self):
        return "4.5 <Country>: Award category distribution for Red / Rose / White wine"

    @property
    def weight(self):
        return 420

    def render(self):
        country_id = self.country

        colors = {
            "RED WINES": self.RED_WINE_WHERE_CLAUSE,
            "WHITE WINES": self.WHITE_WINE_WHERE_CLAUSE,
            "ROSE WINES": self.ROSE_WINE_WHERE_CLAUSE,
        }

        page_info = []

        for color in colors:
            result = {
                "title": color,
            }
            with self.database.connect() as connection:
                res = connection.execute(
                    text("SELECT award.value AS MEDAL, COUNT(award_wine_entity.wine_entity_id) AS WINE_COUNT FROM award_wine_entity "
                    "INNER JOIN wine_entity ON wine_entity.id = award_wine_entity.wine_entity_id "
                    "INNER JOIN wine ON wine.id = wine_entity.wine "
                    "INNER JOIN award ON award.id = award_wine_entity.award_id "
                    "INNER JOIN event ON event.id = award.event_id "
                    f"WHERE (event.year BETWEEN {self.year_from} AND {self.year_to}) AND JSON_UNQUOTE(JSON_EXTRACT(wine.category, '$.\"beverageType\"')) IN (1425) AND {colors[color]} AND wine.country IN ({country_id}) "
                    "GROUP BY award.value"),
                )

            df = pd.DataFrame(res.fetchall(), columns=["MEDAL", "WINE_COUNT"], dtype=int).set_index("MEDAL")
            if df["WINE_COUNT"].sum() != 0:
                df["WINE_COUNT"] = (df["WINE_COUNT"] / df["WINE_COUNT"].sum()) * 100

            buffer = BytesIO()
            self.bar_plot(buffer, df, figsize=(4, 5))
            result["image"] = f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode('utf-8')}"

            page_info.append(result)

        return self.render_template("bar_diagrams/simple.html", page_info=page_info)
