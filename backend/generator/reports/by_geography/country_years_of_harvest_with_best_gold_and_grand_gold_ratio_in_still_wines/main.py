import base64
from io import BytesIO

import pandas as pd
from sqlalchemy import text

from generator.enum import WineType, GWMRUrlRatingType, WineColor
from generator.reports.country_report import CountryReport


class CountryYearsOfHarvestWithBestGoldAndGrandGoldRatioInStillWinesReport(CountryReport):
    @property
    def title(self):
        return "4.5 <Country>: Years of harvest with best Gold and Grand Gold ratio in Still wine"

    @property
    def weight(self):
        return 520

    def render(self):
        colors = {
            "RED": [self.RED_WINE_WHERE_CLAUSE, WineColor.RED],
            "WHITE": [self.WHITE_WINE_WHERE_CLAUSE, WineColor.WHITE],
            "ROSE": [self.ROSE_WINE_WHERE_CLAUSE, WineColor.ROSE],
        }

        page_info = []
        for color in colors:
            category = {
                "title": f"STILL {color} WINES",
            }

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
                        f"           {colors[color][0].replace('wine', 'w')} and "
                        f"           w.country = {self.country} "
                        "    ) and "
                        "    we.vintage > 1900 "
                        "group by we.vintage "
                        "order by count(case when a.value in ('GRAND', 'GOLD') then 1 end) / count(a.value) desc "
                        "limit 8"
                    ),
                )
            top_vintages = res.fetchall()

            category["diagrams"] = []
            for vintage in top_vintages:
                df_pre = pd.DataFrame(index=["GRAND", "GOLD", "SILVER", "BRONZE"])

                diagram = {
                    "title": vintage[0],
                    "link": self.build_top_wines_url(
                        countries_ids=(self.country, ),
                        wine_color=(colors[color][1], ),
                        wine_type=WineType.STILL,
                        event_year=(self.year_from, self.year_to),
                        rating_type=GWMRUrlRatingType.BY_GWMR,
                        vintage=vintage[0],
                    )
                }

                with self.database.connect() as connection:
                    res = connection.execute(
                        text(
                            "SELECT COUNT(award.value) AS MEDAL_COUNT, award.value AS MEDAL_NAME FROM award_wine_entity "
                            "INNER JOIN award ON award.id = award_wine_entity.award_id "
                            "INNER JOIN event ON event.id = award.event_id "
                            "INNER JOIN wine_entity ON wine_entity.id = award_wine_entity.wine_entity_id "
                            f"WHERE (event.year BETWEEN {self.year_from} AND {self.year_to}) AND wine_entity.vintage IN ({vintage[0]}) AND EXISTS("
                            "SELECT * FROM wine "
                            f"WHERE wine.id = wine_entity.wine AND wine.country IN ({self.country}) AND JSON_UNQUOTE(JSON_EXTRACT(wine.category, '$.\"beverageType\"')) IN (1425) AND {colors[color][0]} AND {self.STILL_WINE_WHERE_CLAUSE}) "
                            "GROUP BY award.value"
                        ),
                    )

                df = pd.DataFrame(res.fetchall(), columns=["MEDAL_COUNT", "MEDAL_NAME"]).set_index("MEDAL_NAME")
                df = pd.concat([df_pre, df], axis=1)

                df["MEDAL_COUNT"] = 0 if df["MEDAL_COUNT"].sum() == 0 else (df["MEDAL_COUNT"] / df["MEDAL_COUNT"].sum()) * 100

                buffer = BytesIO()
                self.bar_plot(buffer, df, figsize=(3, 7))
                diagram["image"] = f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode('utf-8')}"

                category["diagrams"].append(diagram)

            page_info.append(category)

        return self.render_template('bar_diagrams/for_some_categories.html', page_info=page_info)
