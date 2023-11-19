import pandas as pd
from sqlalchemy import text

from generator.reports.country_report import CountryReport


class CountryAwardedWinesByRegionReport(CountryReport):
    @property
    def title(self):
        return "4.5 <Country>: Awarded wines by region"

    @property
    def weight(self):
        return 335

    def render(self):
        result = ""

        with self.database.connect() as connection:
            res = connection.execute(
                text(
                    "SELECT COUNT(wine_entity.id) AS AWARDED_WINES FROM wine_entity "
                    "INNER JOIN wine_gwmr ON wine_gwmr.wine_entity_id = wine_entity.id "
                    f"WHERE wine_gwmr.year_from = {self.year_from} AND wine_gwmr.year_to = {self.year_to} AND EXISTS( "
                    "SELECT * FROM wine "
                    f"WHERE wine.id = wine_entity.wine AND JSON_UNQUOTE(JSON_EXTRACT(wine.category, '$.\"beverageType\"')) IN (1425) AND wine.country IN ({self.country})) "
                    "ORDER BY AWARDED_WINES DESC",
                )
            )

        try:
            all_country_wines_count = res.fetchall()[0][0]
        except IndexError:
            return self.render_template("problem.html", problem_message=f"No data about {self.country}")

        with self.database.connect() as connection:
            res = connection.execute(
                text(
                    "SELECT taxonomy_term.name AS REGION_NAME, COUNT(wine_entity.id) AS AWARDED_WINES FROM wine_entity "
                    "INNER JOIN wine_gwmr ON wine_gwmr.wine_entity_id = wine_entity.id "
                    "INNER JOIN taxonomy_term ON taxonomy_term.tid = wine_entity.region "
                    f"WHERE wine_gwmr.year_from = {self.year_from} AND wine_gwmr.year_to = {self.year_to} AND EXISTS( "
                    "SELECT * FROM wine "
                    f"WHERE wine.id = wine_entity.wine AND JSON_UNQUOTE(JSON_EXTRACT(wine.category, '$.\"beverageType\"')) IN (1425) AND wine.country IN ({self.country})) AND taxonomy_term.name != 'Unknown' "
                    "GROUP BY taxonomy_term.tid "
                    "ORDER BY AWARDED_WINES DESC",
                )
            )

        df = pd.DataFrame(res.fetchall(), columns=["REGION_NAME", "AWARDED_WINES"])
        with_region_country_wines_count = sum(df["AWARDED_WINES"])

        if with_region_country_wines_count != 0:
            possible_wines_coefficient = all_country_wines_count / with_region_country_wines_count

            df["POSSIBLE AWARDED_WINES"] = round(df["AWARDED_WINES"] * possible_wines_coefficient)
            new_all_country_wines_count = sum(df["POSSIBLE AWARDED_WINES"])

            result = f"{result}<p>Total in the country: {new_all_country_wines_count}</p>"

        result = f"{result}{df.to_html()}"

        return result
