import pandas as pd
from sqlalchemy import text

from generator.reports.continent_report import ContinentReport


class ContinentReceivedAwardsReport(ContinentReport):
    @property
    def title(self):
        return "4.5 <Continent>: Received Award"

    @property
    def weight(self):
        return 20

    def render(self):
        with self.database.connect() as connection:
            res = connection.execute(
                text("SELECT taxonomy_term.name AS COUNTRY, COUNT(award_wine_entity.award_id) AS MEDAL_COUNT FROM award_wine_entity "
            "INNER JOIN wine_entity ON wine_entity.id = award_wine_entity.wine_entity_id "
            "INNER JOIN wine ON wine.id = wine_entity.wine "
            "INNER JOIN award ON award.id = award_wine_entity.award_id "
            "INNER JOIN event ON event.id = award.event_id "
            "INNER JOIN taxonomy_term ON taxonomy_term.tid = wine.country "
            f"WHERE (event.year BETWEEN {self.year_from} AND {self.year_to}) AND JSON_UNQUOTE(JSON_EXTRACT(wine.category, '$.\"beverageType\"')) IN (1425) AND taxonomy_term.tid IN ({', '.join([str(continent) for continent in self.CONTINENTS[self.continent]])}) "
            "GROUP BY wine.country "
            "ORDER BY MEDAL_COUNT DESC",)
        )
        df = pd.DataFrame(res.fetchall(), columns=["COUNTRY", "MEDAL_COUNT"])

        return f"{df.to_html()}<b>Others are files with zeros</b>"
