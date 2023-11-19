import re

import requests
from sqlalchemy import text

from generator.reports.winery_report import WineryReport


class YourWinesGwmrVivinoCorrelation(WineryReport):
    @property
    def title(self):
        return "8.4 Your Wines GWMR/Vivino correlation"

    @property
    def weight(self):
        return 10

    def render(self):
        type_report = "get_gwmr_vivino_correlation"
        winery = self.winery_id
        year1 = self.year_from
        year2 = self.year_to
        """Your Wines GWMR/Vivino correlation"""
        rating_gwmr_vivino = []
        with (self.database.connect()) as connection:
            query = text(
                "SELECT wine_entity.gwmr,third_party_vivino_wine_entity.vivino_wine_id, third_party_vivino_wine_entity.vivino_vintage_id\
                FROM award_wine_entity\
                INNER JOIN wine_entity ON award_wine_entity.wine_entity_id=wine_entity.id\
                INNER JOIN wine ON wine_entity.wine=wine.id\
                INNER JOIN winery ON wine.winery=winery.id\
                INNER JOIN third_party_vivino_wine_entity ON award_wine_entity.wine_entity_id=third_party_vivino_wine_entity.wine_entity_id\
                INNER JOIN award ON award_wine_entity.award_id=award.id\
                INNER JOIN event ON award.event_id=event.id\
                WHERE (event.year BETWEEN :year_from AND :year_to) AND winery.id = :winery_id\
                GROUP BY award_wine_entity.wine_entity_id"
            ).bindparams(year_from=year1, year_to=year2, winery_id=winery)
            result = connection.execute(query)
            ratings = result.fetchall()
        # Extract vivino rating
        for elem in ratings:
            if elem[2] != None:
                url = f"https://www.vivino.com/external/widgets/vintage?vintage_id={elem[2]}"
            elif elem == None:
                url = f"https://www.vivino.com/external/widgets/vintage?vintage_id={elem[1]}"
            else:
                continue
            user_agent = {'User-agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=user_agent)
            data = response.json()
            rating_vivino = re.findall(r"\d[.]\d*", data["content"])
            if len(rating_vivino) > 0:
                rating_gwmr_vivino.append((float(elem[0]), float(rating_vivino[0])))
        axe_x = []
        axe_y = []
        for r in rating_gwmr_vivino:
            axe_x.append(r[0])
            axe_y.append(r[1])
        name_svg_corelation = "{file_name}.svg".format(
            file_name=self.format_file_name(
                type_report,
                winery,
                year1,
                year2,
                "rating_corelation"
            )
        )
        self.build_scatter(
            axe_x,
            axe_y,
            name_x="GWMR SCORE",
            name_y="VIVINO SCORE",
            name_file=name_svg_corelation
        )
        return self.render_template(
            "report8.4.html",
            year_from=year1,
            year_to=year2,
            report_title=self.title,
            name_svg_corelation=name_svg_corelation
        )
