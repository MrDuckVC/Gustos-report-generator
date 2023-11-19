import pandas as pd
from sqlalchemy import text

from generator.reports.country_report import CountryReport


class CountryMostAwardedOfHarvestForRedRoseWhiteStillWinesReport(CountryReport):
    @property
    def title(self):
        return "4.5 <Country>: Most awarded years of harvest for Red / Rose / White Still wines"

    @property
    def weight(self):
        return 510

    def render(self):
        colors = {
            "Red": self.RED_WINE_WHERE_CLAUSE,
            "White": self.WHITE_WINE_WHERE_CLAUSE,
            "Rose": self.ROSE_WINE_WHERE_CLAUSE,
        }

        result = "<p>All dara in percents</p>"
        for color in colors:
            with self.database.connect() as connection:
                res = connection.execute(
                    text(
                        "SELECT wine_entity.vintage AS VINTAGE, COUNT(award_wine_entity.award_id) AS MEDAL_COUNT FROM award_wine_entity "
                        "INNER JOIN award ON award.id = award_wine_entity.award_id "
                        "INNER JOIN event ON event.id = award.event_id "
                        "INNER JOIN wine_entity ON wine_entity.id = award_wine_entity.wine_entity_id "
                        f"WHERE (event.year BETWEEN {self.year_from} AND {self.year_to}) AND EXISTS( "
                        "SELECT * FROM wine "
                        f"WHERE wine.id = wine_entity.wine AND wine.country IN ({self.country}) AND JSON_UNQUOTE(JSON_EXTRACT(wine.category, '$.\"beverageType\"')) IN (1425) AND {colors[color]} AND {self.STILL_WINE_WHERE_CLAUSE}) AND wine_entity.vintage != 1 "
                        "GROUP BY wine_entity.vintage "
                        "ORDER BY MEDAL_COUNT DESC "
                        "LIMIT 10",
                        ))
            df = pd.DataFrame(res.fetchall(), columns=["VINTAGE", "MEDAL_COUNT"])
            result = f"{result}<div><p>{color} wines</p>{df.to_html()}</div>"

        return result
