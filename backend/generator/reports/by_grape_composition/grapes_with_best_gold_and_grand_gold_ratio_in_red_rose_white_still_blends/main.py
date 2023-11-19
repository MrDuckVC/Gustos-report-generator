import base64
from io import BytesIO

import pandas as pd
from sqlalchemy import text

from generator.reports.report import Report


class GrapesWithBestGoldAndGrandGoldRatioInRedRoseWhiteStillBlends(Report):
    @property
    def title(self):
        return "4.3 Grapes with best Gold and Grand Gold ratio in Red / Rose / White Still Blend"

    @property
    def weight(self):
        return 180

    def render(self):
        colors_ids = {
            "Red": [self.RED_WINE_WHERE_CLAUSE, self.RED_WINE_ID],
            "White": [self.WHITE_WINE_WHERE_CLAUSE, self.WHITE_WINE_ID],
            "Rose": [self.ROSE_WINE_WHERE_CLAUSE, self.ROSE_WINE_ID],
        }

        result = ""

        for color in colors_ids:
            page_info = []
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
                        f"            {self.STILL_WINE_WHERE_CLAUSE.replace('wine', 'w')} and "
                        f"            {colors_ids[color][0].replace('wine', 'w')} "
                        "    ) and "
                        "    exists( "
                        "        select * "
                        "        from wine_grapes wg2 "
                        "        inner join wine_entity we2 on we2.id = wg2.wine_entity "
                        "        where we2.id = we.id "
                        "        group by we2.id "
                        f"       having {self.BLENDS_WINE_HAVING_CLAUSE.replace('wine_grapes', 'wg2')} "
                        "    ) "
                        "group by tt.tid "
                        "having count(a.id) >= 50 "
                        "order by count(case when a.value in ('GRAND', 'GOLD') then 1 end) / count(a.value) desc "
                        "limit 16"
                    )
                )

            for grape, grape_id in res.fetchall():
                df_pre = pd.DataFrame(index=["GRAND", "GOLD", "SILVER", "BRONZE"])

                diagram = {
                    "title": grape,
                    "link": f"https://{self.TOP_WINES_GWMR_DOMEN}/wines?mode=expert&grape[]={grape_id}&grapes_mix[]=blends&co2[]={self.STILL_WINE_ID}&color[]={colors_ids[color][1]}",
                }

                with self.database.connect() as connection:
                    res = connection.execute(
                        text("SELECT award.value AS MEDAL_NAME, COUNT(award.value) AS MEDAL_COUNT FROM award_wine_entity "
                        "INNER JOIN award ON award.id = award_wine_entity.award_id "
                        "INNER JOIN event ON event.id = award.event_id "
                        "INNER JOIN wine_entity ON wine_entity.id = award_wine_entity.wine_entity_id "
                        f"WHERE (event.year BETWEEN {self.year_from} AND {self.year_to}) AND EXISTS( "
                        "SELECT * FROM wine_grapes "
                        f"WHERE wine_grapes.wine_entity = wine_entity.id AND wine_grapes.grape = {grape_id} "
                        "GROUP BY wine_grapes.grape "
                        f"HAVING {self.BLENDS_WINE_HAVING_CLAUSE}) AND EXISTS( "
                        "SELECT * FROM wine "
                        f"WHERE wine.id = wine_entity.wine AND JSON_UNQUOTE(JSON_EXTRACT(wine.category, '$.\"beverageType\"')) IN (1425) AND {colors_ids[color][0]} AND {self.STILL_WINE_WHERE_CLAUSE}) "
                        "GROUP BY MEDAL_NAME"),
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

