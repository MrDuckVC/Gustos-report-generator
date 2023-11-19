import base64
from io import BytesIO

import pandas as pd
from sqlalchemy import text

from generator.enum import GWMRUrlRatingType, WineType, GrapeVariety, WineColor
from generator.reports.country_report import CountryReport


class CountryGrapesWithBestGoldAndGrandGoldRatioInRedRoseWhiteStillWinesReport(CountryReport):
    @property
    def title(self):
        return "4.5 <Country>: Grapes with best Gold and Grand Gold ratio in Red / Rose / White Still Wines"

    @property
    def weight(self):
        return 480

    def render(self):
        colors = {
            "RED": [self.RED_WINE_WHERE_CLAUSE, WineColor.RED],
            "WHITE": [self.WHITE_WINE_WHERE_CLAUSE, WineColor.WHITE],
            "ROSE": [self.ROSE_WINE_WHERE_CLAUSE, WineColor.ROSE],
        }
        grape_mixes = {
            "BLENDS": [self.BLENDS_WINE_HAVING_CLAUSE, GrapeVariety.BLEND],
            "SINGLE": [self.SINGLE_GRAPE_WINE_HAVING_CLAUSE, GrapeVariety.SINGLE],
        }

        result = ""
        for color in colors:
            page_info = []
            for mix in grape_mixes:
                category = {"title": f"{color} STILL {mix}"}

                with self.database.connect() as connection:
                    res = connection.execute(
                        text(
                            "select "
                            "    tt.name as name, "
                            "    tt.tid as id "
                            "from wine_grapes wg "
                            "inner join taxonomy_term tt on tt.tid = wg.grape "
                            "inner join wine_entity we on wg.wine_entity = we.id "
                            "inner join award_wine_entity awe on awe.wine_entity_id = we.id "
                            "inner join award a on a.id = awe.award_id "
                            "where "
                            "    exists( "
                            "        select * "
                            "        from event e "
                            "        where "
                            "            e.id = a.event_id and "
                            f"            (e.year between {self.year_from} and {self.year_to}) "
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
                            "    exists( "
                            "        select * "
                            "        from wine_grapes wg2 "
                            "        inner join wine_entity we2 on we2.id = wg2.wine_entity "
                            "        where we2.id = we.id "
                            "        group by we2.id "
                            f"       having {grape_mixes[mix][0].replace('wine_grapes', 'wg2')} "
                            "    ) "
                            "group by tt.tid "
                            "having count(a.id) >= 2 "
                            "order by count(case when a.value in ('GRAND', 'GOLD') then 1 end) / count(a.value) desc "
                            "limit 16"
                        )
                    )
                top_grapes = res.fetchall()

                category["diagrams"] = []
                for grape, grape_id in top_grapes:
                    df_pre = pd.DataFrame(
                        index=["GRAND", "GOLD", "SILVER", "BRONZE"])

                    diagram = {
                        "title": grape,
                        "link": self.build_top_wines_url(
                            countries_ids=(self.country,),
                            wine_color=(colors[color][1],),
                            wine_type=WineType.STILL,
                            grapes_ids=grape_id,
                            event_year=(self.year_from, self.year_to),
                            rating_type=GWMRUrlRatingType.BY_GWMR,
                        )
                    }

                    with self.database.connect() as connection:
                        res = connection.execute(
                            text(
                                "SELECT COUNT(award.value) AS MEDAL_COUNT, award.value AS MEDAL_NAME FROM award_wine_entity "
                                "INNER JOIN award ON award.id = award_wine_entity.award_id "
                                "INNER JOIN event ON event.id = award.event_id "
                                "INNER JOIN wine_entity ON wine_entity.id = award_wine_entity.wine_entity_id "
                                "INNER JOIN wine_grapes ON wine_grapes.wine_entity = wine_entity.id "
                                f"WHERE (event.year BETWEEN {self.year_from} AND {self.year_to}) AND EXISTS( "
                                "SELECT * FROM wine "
                                f"WHERE wine.id = wine_entity.wine AND JSON_UNQUOTE(JSON_EXTRACT(wine.category, '$.\"beverageType\"')) IN (1425) AND {colors[color][0]} AND {self.STILL_WINE_WHERE_CLAUSE} AND wine.country IN ({self.country})) AND EXISTS( "
                                "SELECT * FROM wine_grapes "
                                f"WHERE wine_grapes.wine_entity = wine_entity.id "
                                "GROUP BY wine_grapes.wine_entity "
                                f"HAVING {grape_mixes[mix][0]}) AND wine_grapes.grape = {grape_id} "
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

            result = f"{result}<h1>{color}</h1>{self.render_template('bar_diagrams/for_some_categories.html', page_info=page_info)}"

        return result
