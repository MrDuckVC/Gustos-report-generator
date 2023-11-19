import base64
from io import BytesIO

import pandas as pd
from sqlalchemy import text

from generator.reports.report import Report


class MedalsAndAwardedWines(Report):
    @property
    def title(self):
        return "3.2 Industry Dynamics: Medals and Awarded wines"

    @property
    def weight(self):
        return 20

    def render(self):
        page_info = []

        with self.database.connect() as connection:
            res = connection.execute(
                text(
                    "SELECT COUNT(DISTINCT award_wine_entity.wine_entity_id) AS AWARDED_WINES_COUNT, COUNT(award_wine_entity.award_id) AS MEDAL_COUNT, event.year AS YEAR FROM award_wine_entity "
                    "INNER JOIN award ON award.id = award_wine_entity.award_id "
                    "INNER JOIN event ON event.id = award.event_id "
                    f"WHERE (event.year BETWEEN {self.year_from} AND {self.year_to}) "
                    "GROUP BY event.year "
                    "ORDER BY event.year DESC"))

        df = pd.DataFrame(res.fetchall(), columns=["AWARDED_WINES_COUNT", "MEDAL_COUNT", "YEAR"], dtype=int).set_index(
            "YEAR")

        buffer = BytesIO()
        self.bar_plot(buffer, df.drop(columns=["AWARDED_WINES_COUNT"]), figsize=(4, 5))
        diagram_competitions = {
            "title": "MEDALS",
            "image": f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode('utf-8')}"
        }

        page_info.append(diagram_competitions)

        buffer = BytesIO()
        self.bar_plot(buffer, df.drop(columns=["MEDAL_COUNT"]), figsize=(4, 5))
        diagram_participants = {
            "title": "AWARDED WINES",
            "image": f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode('utf-8')}"
        }

        page_info.append(diagram_participants)

        return self.render_template("bar_diagrams/industry_dynamics.html", page_info=page_info)
