import base64
from io import BytesIO

import pandas as pd
from sqlalchemy import text

from generator.reports.report import Report


class CompetitionsAndParticipants(Report):
    @property
    def title(self):
        return "3.2 Industry Dynamics: Competitions and Participants"

    @property
    def weight(self):
        return 10

    def render(self):
        page_info = []

        with self.database.connect() as connection:
            res = connection.execute(
                text(
                    "SELECT COUNT(DISTINCT event.id) AS AMOUNT_OF_COMPETITION, COUNT(DISTINCT wine.winery) AS AMOUNT_OF_PARTICIPANTS, event.year AS YEAR FROM wine "
                    "INNER JOIN wine_entity ON wine_entity.wine = wine.id "
                    "INNER JOIN award_wine_entity ON award_wine_entity.wine_entity_id = wine_entity.id "
                    "INNER JOIN award ON award.id = award_wine_entity.award_id "
                    "INNER JOIN event ON award.event_id = event.id "
                    f"WHERE (event.year BETWEEN {self.year_from} AND {self.year_to}) AND JSON_UNQUOTE(JSON_EXTRACT(wine.category, '$.\"beverageType\"')) IN (1425) "
                    "GROUP BY event.year "
                    "ORDER BY event.year DESC"))

        df = pd.DataFrame(res.fetchall(), columns=["AMOUNT_OF_COMPETITION", "AMOUNT_OF_PARTICIPANTS", "YEAR"],
                          dtype=int).set_index("YEAR")

        buffer = BytesIO()
        self.bar_plot(buffer, df.drop(columns=["AMOUNT_OF_PARTICIPANTS"]), figsize=(4, 5))
        diagram_competitions = {
            "title": "COMPETITIONS",
            "image": f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode('utf-8')}"
        }

        page_info.append(diagram_competitions)

        buffer = BytesIO()
        self.bar_plot(buffer, df.drop(columns=["AMOUNT_OF_COMPETITION"]), figsize=(4, 5))
        diagram_participants = {
            "title": "PARTICIPANTS",
            "image": f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode('utf-8')}"
        }

        page_info.append(diagram_participants)

        return self.render_template("bar_diagrams/industry_dynamics.html", page_info=page_info)
