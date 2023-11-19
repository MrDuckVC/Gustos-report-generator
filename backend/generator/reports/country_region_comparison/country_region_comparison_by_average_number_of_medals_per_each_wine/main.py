from sqlalchemy import text

from generator.exceptions import DataNotFoundException
from generator.reports.winery_report import WineryReport
from gustos.utils.file_managed import get_absolute_url


class CountryRegionComparisonByAverageNumberOfMedalsPerEachWine(WineryReport):
    @property
    def title(self):
        return "8.3 Country/Region comparison by average number of medals per each wine"

    @property
    def weight(self):
        return 20

    def render(self, throw_exception=False):
        """Country/Region comparison by average number of medals per each wine"""
        type_report = "get_comparison_comparison_by_average_number_of_medals_per_each_wine"
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

            param_name = "Average number of medals per each wine"
            total_number_of_medal = self.get_total_number_of_medals(winery_id=winery, year1=year1, year2=year2)
            if throw_exception and total_number_of_medal == 0:
                raise DataNotFoundException("No data found.")

            country_id, winery_country = self.get_winery_country_id(winery_id=winery)
            query = text(
                "SELECT count(distinct award_wine_entity.wine_entity_id)\
                FROM award_wine_entity\
                INNER JOIN wine_entity ON award_wine_entity.wine_entity_id=wine_entity.id\
                INNER JOIN wine ON wine_entity.wine=wine.id\
                INNER JOIN winery ON wine.winery=winery.id\
                INNER JOIN award ON award_wine_entity.award_id=award.id\
                INNER JOIN event ON award.event_id=event.id\
                WHERE winery.id = :winery_id AND event.year BETWEEN :year_from AND :year_to"
            ).bindparams(winery_id=winery, year_from=year1, year_to=year2)
            count_wine = connection.execute(query).fetchall()[0][0]
            average_number_of_medal = total_number_of_medal / count_wine

            try:
                query = text(
                    "SELECT we.region as id, r.name as name FROM wine_entity we INNER JOIN wine w ON w.id = we.wine INNER JOIN taxonomy_term r ON r.tid = we.region\
                    WHERE w.winery = :winery_id AND we.region IS NOT NULL GROUP BY we.region ORDER BY COUNT(we.id) DESC LIMIT 1"
                ).bindparams(winery_id=winery)
                region_id, region_name = connection.execute(query).fetchone()

                query = text(
                    "SELECT COUNT(award_wine_entity.wine_entity_id) AS count_medal\
                    FROM award_wine_entity\
                    INNER JOIN wine_entity ON award_wine_entity.wine_entity_id=wine_entity.id\
                    INNER JOIN wine ON wine_entity.wine=wine.id\
                    INNER JOIN winery ON wine.winery=winery.id\
                    INNER JOIN award ON award_wine_entity.award_id=award.id\
                    INNER JOIN event ON award.event_id=event.id\
                    WHERE (event.year BETWEEN :year_from AND :year_to) AND wine_entity.region = :region_id\
                    GROUP BY award_wine_entity.wine_entity_id"
                ).bindparams(year_from=year1, year_to=year2, region_id=region_id)
                data_region = connection.execute(query).fetchall()
                count_medal_by_wine_region = 0
                for m in data_region:
                    count_medal_by_wine_region += m[0]
                region_average_number_of_medal = count_medal_by_wine_region / len(data_region)
                if average_number_of_medal >= region_average_number_of_medal:
                    region_higher_lower_than_the_average = self.higher_than_the_average(average_number_of_medal,
                                                                                        region_average_number_of_medal)
                    cat_region = "Higher than the average in your wine region"
                else:
                    region_higher_lower_than_the_average = self.lower_than_the_average(average_number_of_medal, region_average_number_of_medal)
                    cat_region = "Lower than the average in your region"

                name_svg_region = self.build_bars_base64(
                    a=average_number_of_medal,
                    b=region_average_number_of_medal,
                    winery=winery_name,
                    country_or_region=region_name,
                )
                region_average = round(region_average_number_of_medal, 2)
                region_higher_lower_than_the_average = round(region_higher_lower_than_the_average, 2)
            except TypeError:
                region_higher_lower_than_the_average = None
                cat_region = None
                name_svg_region = None
                region_average = None
                region_average_number_of_medal = None
                region_name = None

            query = text(
                "SELECT COUNT(award_wine_entity.wine_entity_id) AS count_medal\
                FROM award_wine_entity\
                INNER JOIN wine_entity ON award_wine_entity.wine_entity_id=wine_entity.id\
                INNER JOIN wine ON wine_entity.wine=wine.id\
                INNER JOIN winery ON wine.winery=winery.id\
                INNER JOIN award ON award_wine_entity.award_id=award.id\
                INNER JOIN event ON award.event_id=event.id\
                WHERE (event.year BETWEEN :year_from AND :year_to) AND winery.country IN\
                    (SELECT winery.country FROM winery\
                    WHERE winery.id = :winery_id)\
                GROUP BY award_wine_entity.wine_entity_id"
            ).bindparams(year_from=year1, year_to=year2, winery_id=winery)
            data_country = connection.execute(query).fetchall()
        count_medal_by_wine_country = 0
        for m in data_country:
            count_medal_by_wine_country += m[0]
        if throw_exception and count_medal_by_wine_country == 0:
            raise DataNotFoundException("No data found.")
        country_average_number_of_medal = count_medal_by_wine_country / len(data_country)
        if average_number_of_medal >= country_average_number_of_medal:
            country_higher_lower_than_the_average = self.higher_than_the_average(average_number_of_medal,
                                                                                 country_average_number_of_medal)
            cat_country = "Higher than the average in your country"
        else:
            country_higher_lower_than_the_average = self.lower_than_the_average(average_number_of_medal,
                                                                                country_average_number_of_medal)
            cat_country = "Lower than the average in your country"

        name_svg_country = self.build_bars_base64(
            a=average_number_of_medal,
            b=country_average_number_of_medal,
            winery=winery_name,
            country_or_region=winery_country,
        )
        return self.render_template(
            "report8.3.html",
            report_title=self.title,
            total=round(average_number_of_medal, 2),
            region_average=region_average,
            region_higher_lower_than_the_average=region_higher_lower_than_the_average,
            country_average=round(country_average_number_of_medal, 2),
            country_higher_lower_than_the_average=round(country_higher_lower_than_the_average, 2),
            winery_country=winery_country,
            cat_region=cat_region,
            cat_country=cat_country,
            path_to_winery_logo=path_to_winery_logo,
            winery=winery,
            param_name=param_name,
            name_svg_country=name_svg_country,
            name_svg_region=name_svg_region,
            year_from=year1,
            year_to=year2,
            region_average_value=region_average_number_of_medal,
            country_average_value=country_average_number_of_medal,
            average_value=average_number_of_medal,
            region_name=region_name,
            total_description="Average number of medals per each wine",
        )
