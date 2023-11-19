import pandas as pd
from sqlalchemy import text

from generator.reports.report import Report


class TopWineriesInTheWorldByAwardedWines(Report):
    @property
    def title(self):
        return "3.1 Global S & S: Top Wineries in the World by Awarded wines"

    @property
    def weight(self):
        return 90

    def render(self):
        with self.database.connect() as connection:
            res = connection.execute(
                text(
                    "SELECT winery.name AS WINERY_NAME, taxonomy_term.name AS COUNTRY, COUNT(wine_entity.id) AS AWARDED_WINES FROM winery "
                    "INNER JOIN taxonomy_term ON taxonomy_term.tid = winery.country "
                    "INNER JOIN wine ON wine.winery = winery.id "
                    "INNER JOIN wine_entity ON wine_entity.wine = wine.id "
                    "WHERE EXISTS ( "
                    "SELECT * FROM award_wine_entity "
                    "INNER JOIN award ON award.id = award_wine_entity.award_id "
                    "INNER JOIN event ON event.id = award.event_id "
                    f"WHERE award_wine_entity.wine_entity_id = wine_entity.id AND (event.year BETWEEN {self.year_from} AND {self.year_to}) "
                    ") AND JSON_UNQUOTE(JSON_EXTRACT(wine.category, '$.\"beverageType\"')) IN (1425) "
                    "GROUP BY winery.id "
                    "ORDER BY AWARDED_WINES DESC "
                    "LIMIT 5"))

        df = pd.DataFrame(res.fetchall(), columns=["WINERY_NAME", "COUNTRY", "AWARDED_WINES"])

        return df.to_html()
