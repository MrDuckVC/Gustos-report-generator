import pandas as pd
from sqlalchemy import text

from generator.reports.country_report import CountryReport


class CountryReceivedAwardsByRegionReport(CountryReport):
    @property
    def title(self):
        return "4.5 <Country>: Received Awards by region"

    @property
    def weight(self):
        return 330

    def render(self):
        result = ""

        with self.database.connect() as connection:
            res = connection.execute(
                text(
                    "SELECT COUNT(award_wine_entity.award_id) AS AWARD_COUNT FROM award_wine_entity "
                    "INNER JOIN award ON award.id = award_wine_entity.award_id "
                    "INNER JOIN event ON event.id = award.event_id "
                    f"WHERE (event.year BETWEEN {self.year_from} AND {self.year_to}) AND EXISTS( "
                    "SELECT * FROM wine_entity "
                    "INNER JOIN wine ON wine.id = wine_entity.wine "
                    f"WHERE wine_entity.id = award_wine_entity.wine_entity_id AND JSON_UNQUOTE(JSON_EXTRACT(wine.category, '$.\"beverageType\"')) IN (1425) AND wine.country IN ({self.country})) "
                    "ORDER BY AWARD_COUNT DESC",
                    ))

        try:
            all_country_award_count = res.fetchall()[0][0]
        except IndexError:
            return self.render_template("problem.html", problem_message=f"No data about {self.country}")

        with self.database.connect() as connection:
            res = connection.execute(
                text(
                    "SELECT taxonomy_term.name AS REGION_NAME, COUNT(award_wine_entity.award_id) AS AWARD_COUNT FROM award_wine_entity "
                    "INNER JOIN award ON award.id = award_wine_entity.award_id "
                    "INNER JOIN event ON event.id = award.event_id "
                    "INNER JOIN wine_entity ON wine_entity.id = award_wine_entity.wine_entity_id "
                    "INNER JOIN taxonomy_term ON taxonomy_term.tid = wine_entity.region "
                    f"WHERE (event.year BETWEEN {self.year_from} AND {self.year_to}) AND EXISTS( "
                    "SELECT * FROM wine "
                    f"WHERE wine.id = wine_entity.wine AND JSON_UNQUOTE(JSON_EXTRACT(wine.category, '$.\"beverageType\"')) IN (1425) AND wine.country IN ({self.country})) AND taxonomy_term.name != 'Unknown' "
                    "GROUP BY taxonomy_term.tid "
                    "ORDER BY AWARD_COUNT DESC",
                    ))

        df = pd.DataFrame(res.fetchall(), columns=["REGION_NAME", "AWARD_COUNT"])
        with_region_country_award_count = sum(df["AWARD_COUNT"])

        if with_region_country_award_count != 0:
            possible_award_count_coefficient = all_country_award_count / with_region_country_award_count
            df["POSSIBLE AWARD_COUNT"] = round(df["AWARD_COUNT"] * possible_award_count_coefficient)
            new_all_country_award_count = sum(df["POSSIBLE AWARD_COUNT"])
            result = f"{result}<p>Total in the country: {new_all_country_award_count}</p>"

        if all_country_award_count != 0:
            df["POSSIBLE AWARD_COUNT percentage of everything"] = (df["AWARD_COUNT"] / all_country_award_count) * 100

        result = f"{result}{df.to_html()}"

        return result
