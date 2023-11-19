from sqlalchemy import text

from generator.exceptions import DataNotFoundException
from generator.reports.winery_report import WineryReport
from gustos.utils.file_managed import get_absolute_url


class CountryRegionComparisonByAverageGwmrScorePerEachRoseStillWine(WineryReport):
    @property
    def title(self):
        return "8.3 Country/Region comparison by average GWMR Score per each Rose Still wine"

    @property
    def weight(self):
        return 60

    def render(self, throw_exception=False):
        """Country/Region comparison by average GWMR Score per each Rose Still wine"""
        type_report = "get_comparison_by_average_gwmr_score_per_each_rose_still_wine"
        winery = self.winery_id
        year1 = self.year_from
        year2 = self.year_to
        with self.database.connect() as connection:
            query = text(
                "SELECT file_managed.uri, name\
                FROM winery\
                LEFT JOIN file_managed ON winery.logo=file_managed.fid\
                WHERE winery.id = :winery_id"
            ).bindparams(winery_id=winery)
            winery_logo, winery_name = connection.execute(query).fetchone()
            path_to_winery_logo = get_absolute_url(winery_logo)

            param_name = "Average number of medals per each rose still wine"
            country_id, winery_country = self.get_winery_country_id(winery_id=winery)
            query = text(
                "SELECT DISTINCT award_wine_entity.wine_entity_id, wine_entity.gwmr FROM award_wine_entity\
                INNER JOIN wine_entity ON award_wine_entity.wine_entity_id=wine_entity.id\
                INNER JOIN wine ON wine_entity.wine=wine.id\
                INNER JOIN winery ON wine.winery=winery.id\
                INNER JOIN award ON award_wine_entity.award_id=award.id\
                INNER JOIN event ON award.event_id=event.id\
                WHERE winery.id = :winery_id AND event.year BETWEEN :year_from AND :year_to\
                AND wine.color=1171 AND JSON_VALUE(wine.category, '$.co2')=1358 AND wine_entity.gwmr IS NOT NULL"
            ).bindparams(winery_id=winery, year_from=year1, year_to=year2)
            data_gwmr = connection.execute(query).fetchall()
            sum_gwmr = 0
            for gwmr in data_gwmr:
                sum_gwmr += gwmr[1]
            if throw_exception and sum_gwmr == 0:
                raise DataNotFoundException("No data found.")

            count_wine = len(data_gwmr)
            average_gwmr = sum_gwmr / count_wine

            try:
                query = text(
                    "SELECT we.region as id, r.name as name FROM wine_entity we INNER JOIN wine w ON w.id = we.wine INNER JOIN taxonomy_term r ON r.tid = we.region\
                    WHERE w.winery = :winery_id AND we.region IS NOT NULL GROUP BY we.region ORDER BY COUNT(we.id) DESC LIMIT 1"
                ).bindparams(winery_id=winery)
                region_id, region_name = connection.execute(query).fetchone()

                query = text(
                    "SELECT wine_entity.gwmr FROM wine_entity\
                    INNER JOIN wine ON wine_entity.wine=wine.id\
                    INNER JOIN winery ON wine.winery=winery.id\
                    INNER JOIN award_wine_entity ON wine_entity.id=award_wine_entity.wine_entity_id\
                    INNER JOIN award ON award_wine_entity.award_id=award.id\
                    INNER JOIN event ON award.event_id=event.id\
                    WHERE (event.year BETWEEN :year_from AND :year_to) AND wine_entity.region = :region_id\
                    AND wine.color=1171 AND JSON_VALUE(wine.category, '$.co2')=1358 AND wine_entity.gwmr IS NOT NULL\
                    GROUP BY award_wine_entity.wine_entity_id"
                ).bindparams(year_from=year1, year_to=year2, region_id=region_id)
                data_region = connection.execute(query).fetchall()
                count_medal_by_wine_region = 0
                for m in data_region:
                    count_medal_by_wine_region += m[0]
                region_average_gwmr = count_medal_by_wine_region / len(data_region)
                if average_gwmr >= region_average_gwmr:
                    region_higher_lower_than_the_average = self.higher_than_the_average(average_gwmr, region_average_gwmr)
                    cat_region = "Higher than the average in your wine region"
                else:
                    region_higher_lower_than_the_average = self.lower_than_the_average(average_gwmr, region_average_gwmr)
                    cat_region = "Lower than the average in your region"

                name_svg_region = self.build_bars_base64(
                    a=average_gwmr,
                    b=region_average_gwmr,
                    winery=winery_name,
                    country_or_region=region_name,
                )
                region_average = round(region_average_gwmr, 2)
                region_higher_lower_than_the_average = round(region_higher_lower_than_the_average, 2)
            except TypeError:
                region_higher_lower_than_the_average = None
                cat_region = None
                name_svg_region = None
                region_average = None
                region_average_gwmr = None
                region_name = None

            query = text(
                "SELECT wine_entity.gwmr FROM wine_entity\
                INNER JOIN wine ON wine_entity.wine=wine.id\
                INNER JOIN winery ON wine.winery=winery.id\
                INNER JOIN award_wine_entity ON wine_entity.id=award_wine_entity.wine_entity_id\
                INNER JOIN award ON award_wine_entity.award_id=award.id\
                INNER JOIN event ON award.event_id=event.id\
                WHERE (event.year BETWEEN :year_from AND :year_to) AND winery.country IN\
                    (SELECT winery.country FROM winery\
                    WHERE winery.id = :winery_id)\
                AND wine.color=1171 AND JSON_VALUE(wine.category, '$.co2')=1358 AND wine_entity.gwmr IS NOT NULL\
                GROUP BY award_wine_entity.wine_entity_id"
            ).bindparams(winery_id=winery, year_from=year1, year_to=year2)
            data_country = connection.execute(query).fetchall()
        count_medal_by_wine_country = 0
        for m in data_country:
            count_medal_by_wine_country += m[0]
        if throw_exception and count_medal_by_wine_country == 0:
            raise DataNotFoundException("No data found.")
        country_average_gwmr = count_medal_by_wine_country / len(data_country)
        if average_gwmr >= country_average_gwmr:
            country_higher_lower_than_the_average = self.higher_than_the_average(average_gwmr, country_average_gwmr)
            cat_country = "Higher than the average in your country"
        else:
            country_higher_lower_than_the_average = self.lower_than_the_average(average_gwmr, country_average_gwmr)
            cat_country = "Lower than the average in your country"

        name_svg_country = self.build_bars_base64(
            a=average_gwmr,
            b=country_average_gwmr,
            winery=winery_name,
            country_or_region=winery_country,
        )
        return self.render_template(
            "report8.3.html",
            report_title=self.title,
            total=round(average_gwmr, 2),
            region_average=region_average,
            param_name=param_name,
            region_higher_lower_than_the_average=region_higher_lower_than_the_average,
            country_average=round(country_average_gwmr, 2),
            country_higher_lower_than_the_average=round(country_higher_lower_than_the_average, 2),
            winery_country=winery_country,
            cat_region=cat_region,
            cat_country=cat_country,
            path_to_winery_logo=path_to_winery_logo,
            winery=winery,
            name_svg_country=name_svg_country,
            name_svg_region=name_svg_region,
            year_from=year1,
            year_to=year2,
            region_average_value=region_average_gwmr,
            country_average_value=country_average_gwmr,
            average_value=average_gwmr,
            region_name=region_name,
            total_description="Average GWMR per each wine",
        )
