import base64
from io import BytesIO

import pandas as pd
from sqlalchemy import text

from generator.enum import WineType, GWMRUrlRatingType, WineColor
from generator.reports.report import Report


class YearsOfHarvestWithBestGoldAndGrandGoldRatioInRedRoseWhiteStillWines(Report):
    @property
    def title(self):
        return "4.4 Years of harvest with best Gold and Grand Gold ratio in Red / Rose / White Still wine"

    @property
    def weight(self):
        return 20

    def render(self):
        colors_ids = {
            "Red": [self.RED_WINE_WHERE_CLAUSE, WineColor.RED],
            "White": [self.WHITE_WINE_WHERE_CLAUSE, WineColor.WHITE],
            "Rose": [self.ROSE_WINE_WHERE_CLAUSE, WineColor.ROSE],
        }

        result = ""

        for color in colors_ids:
            page_info = []

            with self.database.connect() as connection:
                res = connection.execute(
                    text(
                        "select "
                        "    we.vintage as vintage "
                        "from award_wine_entity awe "
                        "inner join wine_entity we on we.id = awe.wine_entity_id "
                        "inner join award a on a.id = awe.award_id "
                        "where "
                        "    exists( "
                        "        select * "
                        "        from event e "
                        "        where "
                        "            e.id = a.event_id and "
                        f"           (e.year between {self.year_from} and {self.year_to}) "
                        "    ) and "
                        "    exists( "
                        "        select * "
                        "        from wine w "
                        "        where "
                        "            w.id = we.wine and "
                        "            json_unquote(json_extract(w.category, '$.\"beverageType\"')) in (1425) and "
                        f"           {self.STILL_WINE_WHERE_CLAUSE.replace('wine', 'w')} and "
                        f"           {colors_ids[color][0].replace('wine', 'w')} "
                        "    ) and "
                        "    we.vintage > 1900 "
                        "group by we.vintage "
                        "having count(a.value) >= 20 "
                        "order by count(case when a.value in ('GRAND', 'GOLD') then 1 end) / count(a.value) desc "
                        "limit 16"
                    ),
                )

            for vintage in res.fetchall():
                df_pre = pd.DataFrame(index=["GRAND", "GOLD", "SILVER", "BRONZE"])

                diagram = {
                    "title": vintage[0],
                    "link": self.build_top_wines_url(
                        wine_color=(colors_ids[color][1],),
                        wine_type=WineType.STILL,
                        event_year=(self.year_from, self.year_to),
                        rating_type=GWMRUrlRatingType.BY_GWMR,
                        vintage=vintage[0],
                    ),
                }

                with self.database.connect() as connection:
                    res = connection.execute(
                        text(
                            "SELECT award.value AS MEDAL_NAME, COUNT(award.value) AS MEDAL_COUNT FROM award_wine_entity "
                            "INNER JOIN award ON award.id = award_wine_entity.award_id "
                            "INNER JOIN event ON event.id = award.event_id "
                            "INNER JOIN wine_entity ON wine_entity.id = award_wine_entity.wine_entity_id "
                            f"WHERE (event.year BETWEEN {self.year_from} AND {self.year_to}) AND EXISTS( "
                            "SELECT * FROM wine "
                            f"WHERE wine.id = wine_entity.wine AND JSON_UNQUOTE(JSON_EXTRACT(wine.category, '$.\"beverageType\"')) IN (1425) AND {colors_ids[color][0]} AND {self.STILL_WINE_WHERE_CLAUSE}) AND wine_entity.vintage = {vintage[0]} "
                            "GROUP BY MEDAL_NAME"
                        ),
                    )

                df = pd.DataFrame(res.fetchall(), columns=["MEDAL_NAME", "MEDAL_COUNT"]).set_index("MEDAL_NAME")
                df = pd.concat([df_pre, df], axis=1)

                df["MEDAL_COUNT"] = 0 if df["MEDAL_COUNT"].sum() == 0 else (df["MEDAL_COUNT"] / df["MEDAL_COUNT"].sum()) * 100

                buffer = BytesIO()
                self.bar_plot(buffer, df, figsize=(3, 7))
                diagram["image"] = f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode('utf-8')}"
                page_info.append(diagram)

            result = f"{result}<h1>{color}</h1>{self.render_template('bar_diagrams/for_one_category.html', page_info=page_info)}"

        return result
