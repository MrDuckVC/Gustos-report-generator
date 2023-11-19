import pandas as pd
from sqlalchemy import text

from generator.reports.continent_report import ContinentReport


class ContinentCompetitionsAndMedalsReport(ContinentReport):
    @property
    def title(self):
        return "4.5 <Continent>: Competitions and Medal"

    @property
    def weight(self):
        return 10

    def render(self):
        with self.database.connect() as connection:
            res = connection.execute(
                text("SELECT taxonomy_term.name AS COUNTRY, COUNT(award_wine_entity.award_id) AS MEDAL_COUNT FROM event "
            "INNER JOIN award ON award.event_id = event.id "
            "INNER JOIN award_wine_entity ON award_wine_entity.award_id = award.id "
            "INNER JOIN taxonomy_term ON taxonomy_term.tid = event.country_id "
            f"WHERE (event.year BETWEEN {self.year_from} AND {self.year_to}) AND EXISTS( "
            "SELECT * FROM wine "
            "INNER JOIN wine_entity ON wine_entity.wine = wine.id "
            f"WHERE wine_entity.id = award_wine_entity.wine_entity_id AND JSON_UNQUOTE(JSON_EXTRACT(wine.category, '$.\"beverageType\"')) IN (1425)) AND taxonomy_term.tid IN ({', '.join([str(continent) for continent in self.CONTINENTS[self.continent]])}) "
            "GROUP BY event.country_id "
            "ORDER BY MEDAL_COUNT DESC"
        ))
        df = pd.DataFrame(res.fetchall(), columns=["COUNTRY", "MEDAL_COUNT"])

        return f"{df.to_html()}<b>Others are filled with zeros</b>"
