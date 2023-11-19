from functools import reduce

from sqlalchemy import func, select, text

from generator.reports.winery_report import WineryReport
from generator.utils.formatting import format_entity_name

from gustos.models import (
    file_managed, wine_entity,
    taxonomy_term, award,
    award_wine_entity, event,
    winery, wine,
)
from gustos.utils.file_managed import get_absolute_url


class YourWineryProfile(WineryReport):
    @property
    def title(self):
        return "8 Your Winery Profile"

    @property
    def weight(self):
        return 10

    def render(self):
        year1 = self.year_from
        year2 = self.year_to
        with (self.database.connect()) as connection:
            v = winery.alias("v")
            fm = file_managed.alias("fm")
            tt = taxonomy_term.alias("tt")
            query = select(
                v.c.name,
                tt.c.name,
                fm.c.uri,
            ).select_from(v) \
                .join(tt, tt.c.tid == v.c.country, isouter=True) \
                .join(fm, fm.c.fid == v.c.logo, isouter=True) \
                .where(v.c.id == self.winery_id)
            result = connection.execute(query)
            winery_name, producer_country, winery_logo = result.fetchone()

            path_to_winery_logo = get_absolute_url(winery_logo)

            w = wine.alias("w")
            query = select(
                tt.c.name,
            ).select_from(w) \
                .join(tt, tt.c.tid == w.c.country, isouter=True) \
                .where(w.c.winery == self.winery_id) \
                .group_by(tt.c.name) \
                .order_by(func.count(w.c.id.distinct()).desc())
            result = connection.execute(query)
            wine_origin = ", ".join([c for c, in result.fetchall()])

            # GET Total number of medals
            total_medals = self.get_total_number_of_medals(winery_id=self.winery_id, year1=year1, year2=year2)
            # Get Total medals by type

            awe = award_wine_entity.alias("awe")
            a = award.alias("a")
            e = event.alias("e")
            we = wine_entity.alias("we")
            query = select(
                a.c.value,
                func.count(a.c.value),
            ).select_from(awe) \
                .join(a, a.c.id == awe.c.award_id) \
                .join(e, e.c.id == a.c.event_id) \
                .join(we, we.c.id == awe.c.wine_entity_id) \
                .join(w, w.c.id == we.c.wine) \
                .where(
                w.c.winery == self.winery_id,
                    e.c.year.between(self.year_from, self.year_to)
                ) \
                .group_by(a.c.value)
            result = connection.execute(query)
            total_medals_by_type = result.fetchall()
            grand_medal = ""
            gold_medal = ""
            silver_medal = ""
            bronze_medal = ""
            percent_grand = 0
            percent_gold = 0
            percent_silver = 0
            percent_bronze = 0
            for medal in total_medals_by_type:
                if medal[0] == "GRAND":
                    grand_medal = medal[1]
                    percent_grand += self.calc_percentages(
                        total_medals, grand_medal)
                elif medal[0] == "GOLD":
                    gold_medal = medal[1]
                    percent_gold += self.calc_percentages(total_medals, gold_medal)
                elif medal[0] == "SILVER":
                    silver_medal = medal[1]
                    percent_silver += self.calc_percentages(
                        total_medals, silver_medal)
                elif medal[0] == "BRONZE":
                    bronze_medal = medal[1]
                    percent_bronze += self.calc_percentages(
                        total_medals, bronze_medal)
            # GET Number of competitions
            query = text(
                "SELECT \
                    COUNT(DISTINCT e.id), \
                    CASE \
                        WHEN c.region = 'WEST_EUROPE' THEN 'Europe' \
                        WHEN c.region = 'EAST_EUROPE' THEN 'Europe' \
                        WHEN c.region = 'NORTH_AMERICA' THEN 'North America' \
                        WHEN c.region = 'AFRICA' THEN 'Africa' \
                        WHEN c.region = 'SOUTH_AMERICA' THEN 'South America' \
                        WHEN c.region = 'ASIA' THEN 'Asia' \
                        WHEN c.region = 'AUSTRALIA' THEN 'Pacific' \
                        ELSE 'Other' \
                    END AS final_region \
                FROM winery v \
                INNER JOIN wine w ON v.id=w.winery \
                INNER JOIN wine_entity we ON w.id=we.wine \
                INNER JOIN award_wine_entity awe ON we.id=awe.wine_entity_id \
                INNER JOIN award a ON awe.award_id=a.id \
                INNER JOIN event e ON a.event_id=e.id \
                INNER JOIN competition c ON e.competition_id=c.id \
                WHERE v.id = :winery_id AND (e.year BETWEEN :year_from AND :year_to) \
                GROUP BY final_region"
            ).bindparams(winery_id=self.winery_id, year_from=year1, year_to=year2)
            result = connection.execute(query)
            total_competitions_by_continent = result.fetchall()
            # Calculate total number of competitions.
            total_competitions = reduce(lambda result, data: result + data[0], total_competitions_by_continent, 0)

            # GET Number of Grape varieties of awarded wines
            query = text(
                "SELECT COUNT(DISTINCT wine_grapes.grape), taxonomy_term.name\
                FROM wine_grapes\
                INNER JOIN wine_entity ON wine_grapes.wine_entity=wine_entity.id\
                INNER JOIN wine ON wine_entity.wine=wine.id\
                INNER JOIN taxonomy_term ON wine.color=taxonomy_term.tid\
                INNER JOIN award_wine_entity ON wine_entity.id=award_wine_entity.wine_entity_id\
                INNER JOIN award ON award_wine_entity.award_id=award.id\
                INNER JOIN event ON award.event_id=event.id\
                WHERE wine_grapes.wine_entity IN \
                    (SELECT wine_entity.id\
                    FROM wine_entity\
                    INNER JOIN wine ON wine_entity.wine=wine.id\
                    INNER JOIN winery ON wine.winery=winery.id\
                    WHERE winery.id = :winery_id) AND\
                    (event.year BETWEEN :year_from AND :year_to)\
                GROUP BY wine.color;"
            ).bindparams(winery_id=self.winery_id, year_from=year1, year_to=year2)
            result = connection.execute(query)
            grape_varieties_by_type = result.fetchall()
            query = text(
                "SELECT COUNT(distinct wine_grapes.grape)\
                FROM wine_grapes\
                INNER JOIN wine ON wine_grapes.wine=wine.id\
                INNER JOIN award_wine_entity ON wine_grapes.wine_entity=award_wine_entity.wine_entity_id\
                INNER JOIN award ON award_wine_entity.award_id=award.id\
                INNER JOIN event ON award.event_id=event.id\
                INNER JOIN winery ON wine.winery=winery.id\
                WHERE winery.id = :winery_id AND event.year BETWEEN :year_from AND :year_to"
            ).bindparams(winery_id=self.winery_id, year_from=year1, year_to=year2)
            result = connection.execute(query)
            total_grape_varieties, = result.fetchone()
            # GET number of awarded wines
            awarded_wines = {"blend": [], "single_variety": []}
            still_red_blends = 0
            still_red_sv = 0
            still_white_blends = 0
            still_white_sv = 0
            still_rose_blends = 0
            still_rose_sv = 0
            sparkling_pearl_white = 0
            sparkling_pearl_rose = 0
            query = text(
                "SELECT taxonomy_term.name, wine.color\
                FROM award_wine_entity\
                INNER JOIN wine_entity ON award_wine_entity.wine_entity_id=wine_entity.id\
                INNER JOIN wine ON wine_entity.wine=wine.id\
                INNER JOIN winery ON wine.winery=winery.id\
                INNER JOIN taxonomy_term ON JSON_VALUE(wine.category, '$.co2')=taxonomy_term.tid\
                INNER JOIN wine_grapes ON wine_entity.id=wine_grapes.wine_entity\
                INNER JOIN award ON award_wine_entity.award_id=award.id\
                INNER JOIN event ON award.event_id=event.id\
                WHERE winery.id = :winery_id AND (event.year BETWEEN :year_from AND :year_to) AND award_wine_entity.wine_entity_id IN\
                    (SELECT DISTINCT wine_entity.id\
                    FROM wine_entity\
                    INNER JOIN wine_grapes ON wine_entity.id=wine_grapes.wine_entity\
                    INNER JOIN wine ON wine_entity.wine=wine.id\
                    WHERE (wine_grapes.percent<85 OR wine_grapes.percent=0) AND wine_entity.id IN\
                        (SELECT wine_grapes.wine_entity\
                        FROM wine_grapes\
                        GROUP BY wine_grapes.wine_entity\
                        HAVING COUNT(wine_grapes.grape)>1\
                        )\
                    )\
                GROUP BY wine_grapes.wine_entity"
            ).bindparams(winery_id=self.winery_id, year_from=year1, year_to=year2)
            result = connection.execute(query)
            awarded_wines["blend"] = result.fetchall()
            query = text(
                "SELECT taxonomy_term.name, wine.color\
                FROM award_wine_entity\
                INNER JOIN wine_entity ON award_wine_entity.wine_entity_id=wine_entity.id\
                INNER JOIN wine ON wine_entity.wine=wine.id\
                INNER JOIN winery ON wine.winery=winery.id\
                INNER JOIN taxonomy_term ON JSON_VALUE(wine.category, '$.co2')=taxonomy_term.tid\
                INNER JOIN wine_grapes ON wine_entity.id=wine_grapes.wine_entity\
                INNER JOIN award ON award_wine_entity.award_id=award.id\
                INNER JOIN event ON award.event_id=event.id\
                WHERE winery.id = :winery_id AND (event.year BETWEEN :year_from AND :year_to) AND award_wine_entity.wine_entity_id IN\
                    (SELECT DISTINCT wine_entity.id\
                    FROM wine_entity\
                    INNER JOIN wine_grapes ON wine_entity.id=wine_grapes.wine_entity\
                    INNER JOIN wine ON wine_entity.wine=wine.id\
                    WHERE (wine_grapes.percent>85 OR wine_grapes.percent=0) AND wine_entity.id IN\
                        (SELECT wine_grapes.wine_entity\
                        FROM wine_grapes\
                        GROUP BY wine_grapes.wine_entity\
                        HAVING COUNT(wine_grapes.grape)=1\
                        )\
                    )\
                GROUP BY wine_grapes.wine_entity"
            ).bindparams(winery_id=self.winery_id, year_from=year1, year_to=year2)
            result = connection.execute(query)
            awarded_wines["single_variety"] = result.fetchall()
        total_awarded_wines = len(awarded_wines["blend"]) + len(awarded_wines["single_variety"])
        if len(awarded_wines["blend"]) > 0:
            for row in awarded_wines["blend"]:
                if (row[0] == "Still wine (CO2 less than 0.5 bar)") and (str(row[1]) == self.WHITE_WINE_ID):
                    still_white_blends += 1
                elif (row[0] == "Still wine (CO2 less than 0.5 bar)") and (str(row[1]) == self.ROSE_WINE_ID):
                    still_rose_blends += 1
                elif (row[0] == "Still wine (CO2 less than 0.5 bar)") and (str(row[1]) == self.RED_WINE_ID):
                    still_red_blends += 1
                elif (row[0] == "Sparkling wine (CO2 more than 2.5 bar)" or row[0] == "Pearl wine (CO2 between 0.5 - 2.5 bar)") and str(row[1]) == self.ROSE_WINE_ID:
                    sparkling_pearl_rose += 1
                elif (row[0] == "Sparkling wine (CO2 more than 2.5 bar)" or row[0] == "Pearl wine (CO2 between 0.5 - 2.5 bar)") and str(row[1]) == self.WHITE_WINE_ID:
                    sparkling_pearl_white += 1
            still_white_blends_percent = self.calc_percentages(total_awarded_wines, still_white_blends)
            still_red_blends_percent = self.calc_percentages(total_awarded_wines, still_red_blends)
            still_rose_blends_percent = self.calc_percentages(total_awarded_wines, still_rose_blends)
        else:
            still_white_blends_percent = ""
            still_red_blends_percent = ""
            still_rose_blends_percent = ""
        if len(awarded_wines["single_variety"]) > 0:
            for row in awarded_wines["single_variety"]:
                if (row[0] == "Sparkling wine (CO2 more than 2.5 bar)" or row[0] == "Pearl wine (CO2 between 0.5 - 2.5 bar)") and (str(row[1]) == self.ROSE_WINE_ID):
                    sparkling_pearl_rose += 1
                elif (row[0] == "Sparkling wine (CO2 more than 2.5 bar)" or row[0] == "Pearl wine (CO2 between 0.5 - 2.5 bar)") and (str(row[1]) == self.WHITE_WINE_ID):
                    sparkling_pearl_white += 1
                elif (row[0] == "Still wine (CO2 less than 0.5 bar)") and (str(row[1]) == self.WHITE_WINE_ID):
                    still_white_sv += 1
                elif (row[0] == "Still wine (CO2 less than 0.5 bar)") and (str(row[1]) == self.ROSE_WINE_ID):
                    still_rose_sv += 1
                elif (row[0] == "Still wine (CO2 less than 0.5 bar)") and (str(row[1]) == self.RED_WINE_ID):
                    still_red_sv += 1
            sparkling_pearl_white_percent = self.calc_percentages(total_awarded_wines, sparkling_pearl_white)
            sparkling_pearl_rose_percent = self.calc_percentages(total_awarded_wines, sparkling_pearl_rose)
            still_rose_sv_percent = self.calc_percentages(total_awarded_wines, still_rose_sv)
            still_white_sv_percent = self.calc_percentages(total_awarded_wines, still_white_sv)
            still_red_sv_percent = self.calc_percentages(total_awarded_wines, still_red_sv)

        else:
            sparkling_pearl_white_percent = ""
            sparkling_pearl_rose_percent = ""
            still_white_sv_percent = ""
            still_red_sv_percent = ""
            still_rose_sv_percent = ""
        return self.render_template(
            "report8.0.html",
            report_title=self.title,
            producer_country=producer_country,
            wine_origin=wine_origin,
            total_medals=total_medals,
            grand_medal=grand_medal,
            gold_medal=gold_medal,
            silver_medal=silver_medal,
            bronze_medal=bronze_medal,
            percent_grand=percent_grand,
            percent_gold=percent_gold,
            percent_silver=percent_silver,
            percent_bronze=percent_bronze,
            year_from=year1,
            year_to=year2,
            total_competitions_by_continent=total_competitions_by_continent,
            total_competitions=total_competitions,
            grape_varieties_by_type=grape_varieties_by_type,
            total_grape_varieties=total_grape_varieties,
            stil_red_blends=still_red_blends,
            stil_red_sv=still_red_sv,
            stil_white_blends=still_white_blends,
            stil_white_sv=still_white_sv,
            stil_rose_blends=still_rose_blends,
            stil_rose_sv=still_rose_sv,
            sparklingpearl_white=sparkling_pearl_white,
            sparklingpearl_rose=sparkling_pearl_rose,
            total_awarded_wines=total_awarded_wines,
            stil_white_blends_percent=still_white_blends_percent,
            stil_red_sv_percent=still_red_sv_percent,
            stil_white_sv_percent=still_white_sv_percent,
            stil_red_blends_percent=still_red_blends_percent,
            stil_rose_sv_percent=still_rose_sv_percent,
            stil_rose_blends_percent=still_rose_blends_percent,
            sparklingpearl_white_percent=sparkling_pearl_white_percent,
            sparklingpearl_rose_percent=sparkling_pearl_rose_percent,
            path_to_winery_logo=path_to_winery_logo,
            winery_name=format_entity_name(winery_name),
        )
