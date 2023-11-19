import pandas as pd
from sqlalchemy import text

from generator.reports.country_report import CountryReport


class CountryIconicWinesWinesDistributionReport(CountryReport):
    @property
    def title(self):
        return "4.5 <Country>: “Iconic wines” wines distribution"

    @property
    def weight(self):
        return 350

    def render(self):
        result = ""

        with self.database.connect() as connection:
            res = connection.execute(
                text(
                    f"SELECT COUNT(CASE WHEN {self.ICONIC_WINES_WHERE_CLAUSE} THEN 1 END) AS WITH_HIGH_GWMR_SCORE, COUNT(wine_gwmr.rating) AS WITH_ALL_GWMR_SCORE FROM wine_entity "
                    "INNER JOIN wine_gwmr ON wine_gwmr.wine_entity_id = wine_entity.id "
                    "INNER JOIN wine ON wine.id = wine_entity.wine "
                    f"WHERE wine_gwmr.year_from = {self.year_from} AND wine_gwmr.year_to = {self.year_to} AND wine.country IN ({self.country}) AND JSON_UNQUOTE(JSON_EXTRACT(wine.category, '$.\"beverageType\"')) IN (1425) "
                    "ORDER BY WITH_HIGH_GWMR_SCORE DESC",
                )
            )

        country_with_height_gwmr_score, country_with_all_gwmr_score = res.fetchall()[0]

        with self.database.connect() as connection:
            res = connection.execute(
                text(
                    f"SELECT taxonomy_term.name AS REGION, COUNT(CASE WHEN {self.ICONIC_WINES_WHERE_CLAUSE} THEN 1 END) AS WITH_HIGH_GWMR_SCORE, COUNT(wine_gwmr.rating) AS WITH_ALL_GWMR_SCORE FROM wine_entity "
                    "INNER JOIN wine_gwmr ON wine_gwmr.wine_entity_id = wine_entity.id "
                    "INNER JOIN wine ON wine.id = wine_entity.wine "
                    "INNER JOIN taxonomy_term ON taxonomy_term.tid = wine_entity.region "
                    f"WHERE wine_gwmr.year_from = {self.year_from} AND wine_gwmr.year_to = {self.year_to} AND wine.country IN ({self.country}) AND JSON_UNQUOTE(JSON_EXTRACT(wine.category, '$.\"beverageType\"')) IN (1425) AND taxonomy_term.name != 'Unknown' "
                    "GROUP BY wine_entity.region "
                    "ORDER BY WITH_HIGH_GWMR_SCORE DESC, WITH_ALL_GWMR_SCORE DESC",
                )
            )

        df = pd.DataFrame(res.fetchall(), columns=["REGION", "WITH_HIGH_GWMR_SCORE", "WITH_ALL_GWMR_SCORE"])

        with_region_country_with_height_gwmr_score = sum(df["WITH_HIGH_GWMR_SCORE"])
        if with_region_country_with_height_gwmr_score != 0:
            possible_with_height_gwmr_score_coefficient = country_with_height_gwmr_score / with_region_country_with_height_gwmr_score
            df["POSSIBLE WITH_HIGH_GWMR_SCORE"] = round(
                df["WITH_HIGH_GWMR_SCORE"] * possible_with_height_gwmr_score_coefficient)

        with_region_country_with_all_gwmr_score = sum(df["WITH_ALL_GWMR_SCORE"])
        if with_region_country_with_all_gwmr_score != 0:
            possible_with_all_gwmr_score_coefficient = country_with_all_gwmr_score / with_region_country_with_all_gwmr_score
            df["POSSIBLE WITH_ALL_GWMR_SCORE"] = round(
                df["WITH_ALL_GWMR_SCORE"] * possible_with_all_gwmr_score_coefficient)

        result = f"{result}<p>Total in the country POSSIBLE WITH_HIGH_GWMR_SCORE: {country_with_height_gwmr_score}</p>" \
                 f"<p>Total in the country POSSIBLE WITH_ALL_GWMR_SCORE: {country_with_all_gwmr_score}</p>"

        result = f"{result}{df.to_html()}"

        return f"{result}<b>Others are files with zeros</b>"
