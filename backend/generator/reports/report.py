import os
import re
from abc import ABC, abstractmethod
from hashlib import sha1
from typing import Any, Sequence, Tuple, List, IO
from urllib.parse import urlencode, urlunsplit

import matplotlib as mpl
import pandas as pd
from django.conf import settings
from django.forms import Form
from django.http import HttpRequest
from django.template.loader import render_to_string
from matplotlib import pyplot as plt
from sqlalchemy import Integer, select, Select, case, Case, Column
from sqlalchemy.sql import func

from generator.forms import DefaultReportForm
from generator.enum import WineType, WineColor, GrapeVariety, Continent, GWMRUrlRatingType, BeverageType
from generator.utils.database import apply_range_filter, Database
from gustos.models import (
    wine, wine_entity,
    wine_grapes, taxonomy_term,
    award, award_wine_entity,
    event, wine_gwmr,
)


class Report(ABC):
    """
    Abstract class for reports.
    """
    STILL_WINE_ID = "1358"
    SPARKLING_PEARL_WINE_IDS = ["1359", "1360"]
    STILL_WINE_WHERE_CLAUSE = f"JSON_UNQUOTE(JSON_EXTRACT(wine.category, '$.\"co2\"')) IN ({STILL_WINE_ID})"
    SPARKLING_PEARL_WINE_WHERE_CLAUSE = f"JSON_UNQUOTE(JSON_EXTRACT(wine.category, '$.\"co2\"')) IN ({', '.join(SPARKLING_PEARL_WINE_IDS)})"
    RED_WINE_ID = "1169"
    WHITE_WINE_ID = "1170"
    ROSE_WINE_ID = "1171"
    RED_WINE_WHERE_CLAUSE = f"JSON_UNQUOTE(JSON_EXTRACT(wine.category, '$.\"color\"')) IN ({RED_WINE_ID})"
    WHITE_WINE_WHERE_CLAUSE = f"JSON_UNQUOTE(JSON_EXTRACT(wine.category, '$.\"color\"')) IN ({WHITE_WINE_ID})"
    ROSE_WINE_WHERE_CLAUSE = f"JSON_UNQUOTE(JSON_EXTRACT(wine.category, '$.\"color\"')) IN ({ROSE_WINE_ID})"
    BLENDS_WINE_HAVING_CLAUSE = "MAX(wine_grapes.percent) <= 85"
    SINGLE_GRAPE_WINE_HAVING_CLAUSE = "MAX(wine_grapes.percent) > 85"
    SINGLE_GRAPE_WHERE_EXISTS_CLAUSE = "wine_grapes.percent > 85"
    ICONIC_WINES_WHERE_CLAUSE = "wine_gwmr.rating > 90"

    TOP_WINES_GWMR_DOMAIN = "gwmr.local"

    CONTINENTS = {
        Continent.AFRICA.value:
            (923, 926, 943, 949, 955, 956, 958, 960, 962, 963, 969, 970, 971, 974, 981, 985, 987, 988, 990, 999, 1000, 1003, 1012, 1013, 1035, 1044, 1045, 1046, 1052, 1053, 1056, 1060, 1061, 1062, 1070, 1071, 1073, 1080, 1081, 1100, 1103,
             1105, 1113, 1115, 1117, 1118, 1124, 1125, 1127, 1130, 1133, 1139, 1142, 1146, 1151, 1165, 1167, 1168),
        Continent.ASIA.value:
            (920, 931, 935, 937, 938, 945, 952, 953, 957, 965, 966, 967, 1001, 1019, 1022, 1023, 1024, 1025, 1028, 1031, 1033, 1034, 1037, 1038, 1039, 1040, 1041, 1043, 1050, 1054, 1055, 1067, 1072, 1075, 1086, 1087, 1089, 1094, 1099, 1114,
             1119, 5103, 1129, 1136, 1137, 1138, 1140, 1141, 1147, 1148, 1153, 1158, 1161, 1166),
        Continent.EUROPE.value:
            (1051, 2717, 921, 922, 925, 934, 940, 941, 948, 954, 975, 978, 979, 980, 989, 992, 994, 995, 1002, 1004, 1005, 1011, 1017, 1020, 1021, 1026, 1027, 1029, 1032, 6958, 1042, 1047, 1048, 1049, 1057, 1065, 1066, 1068, 1076, 1085,
             1096, 1097, 1101, 1112, 1116, 1121, 1122, 1128, 1132, 1134, 1135, 1152, 1154, 1102),
        Continent.NORTH_AMERICA.value:
            (927, 929, 936, 939, 942, 944, 959, 961, 973, 976, 982, 983, 986, 1006, 1007, 1008, 1010, 1015, 1018, 1030, 1059, 1063, 1069, 1079, 1090, 1098, 1104, 1106, 1107, 1108, 1109, 1110, 1120, 1149, 1155, 1156, 1162, 1163),
        Continent.PACIFIC.value:
            (924, 933, 972, 993, 997, 1009, 1016, 1036, 1058, 1064, 1074, 1077, 1078, 1082, 1083, 1084, 1088, 1091, 1095, 1111, 1123, 1143, 1144, 1150, 1159, 1164),
        Continent.SOUTH_AMERICA.value:
            (930, 932, 946, 947, 951, 964, 968, 977, 984, 991, 996, 1014, 1092, 1093, 1131, 1145, 1157, 1160)
    }

    def get_graphic_path(self, file_name_part: str) -> str:
        """
        Get path to file.

        :param file_name_part: string - file name part.

        :return: string - path to file.
        """
        return os.path.join(settings.MEDIA_ROOT, "graphics", file_name_part).replace("/var/www/backend/", "")

    def get_countries_names(self):
        """
        Get list of all countries names.

        :return: list of string.
        """
        with self.database.connect() as connection:
            query = select(taxonomy_term.c.name).select_from(taxonomy_term).where(taxonomy_term.c.vid == 3)
            result = connection.execute(query)
            return [country for country, in result.fetchall()]

    def prepare_for_path(self, file_name_part: str) -> str:
        """
        Prepare string for path.

        :param file_name_part: string - file name part.

        :return: string - prepared string.
        """
        return re.sub(r"[^a-zA-Z0-9_-]", "", file_name_part)

    def get_country_id(self, country_name):
        with self.database.connect() as connection:
            query = select(taxonomy_term.c.tid).select_from(taxonomy_term).where(taxonomy_term.c.name == country_name, taxonomy_term.c.vid == 3).limit(1)
            result = connection.execute(query)
            return result.fetchone()

    def pie_plot(self, output: IO, df: pd.DataFrame, figsize, title: str = "", legend: bool or str = False, startangle: int = 240, show_labels=True):
        if show_labels:
            labels = df.index
        else:
            labels = None
        try:
            df.plot.pie(
                title=title, subplots=True, figsize=figsize, startangle=startangle,
                counterclock=False, legend=legend, autopct="%1.2f%%", labels=labels
            )
        except (ValueError, TypeError):
            return self.render_template("problem.html", problem_message="No data")

        plt.savefig(output, bbox_inches="tight")
        plt.close()

    def bar_plot(self, output: IO, df: pd.DataFrame, figsize, title: str = "", legend: bool or str = False):
        try:
            ax = df.plot.bar(rot=0, figsize=figsize, title=title, legend=legend)
        except Exception as e:
            print(e)
            return None

        ax.set(xlabel=None)

        for container in ax.containers:
            ax.bar_label(container)

        plt.savefig(output, bbox_inches="tight")
        plt.close()

    def build_query_for_wine_entity(
            self,
            select_fields: Tuple[Any, ...] = None,
            countries: Tuple[int, ...] | int = None,
            event_year: Tuple[int, int] = None,
            wine_color: Tuple[WineColor, ...] | WineColor = None,
            wine_type: Tuple[WineType, ...] | WineType = None,
            grape_variety: GrapeVariety = None,
            gwmr: Tuple[float, float] = None,
            we=wine_entity.alias("we"),
            w=wine.alias("w"),
            wg=wine_grapes.alias("wg"),
            awe=award_wine_entity.alias("awe"),
            a=award.alias("a"),
            e=event.alias("e"),
            wgwmr=wine_gwmr.alias("wgwmr"),
    ) -> Select:
        """
        Builds SQLAlchemy query which selects information about wine entities.
        """
        if select_fields is None:
            select_fields = (we,)

        query = select(
            *select_fields
        ).select_from(we) \
            .join(w, w.c.id == we.c.wine) \
            .where(func.json_value(w.c.category, "$.beverageType").cast(Integer) == BeverageType.WINE)

        if countries is not None:
            if not isinstance(countries, Sequence):
                countries = (countries,)

            query = query.where(w.c.country.in_(countries))

        if wine_color is not None:
            if not isinstance(wine_color, Sequence):
                wine_color = (wine_color,)
            wine_color = tuple((wc.value if isinstance(wc, WineColor) else wc for wc in wine_color))
            if len(wine_color) > 0:
                query = query.where(func.json_value(w.c.category, "$.color").in_(wine_color))

        if wine_type is not None:
            if not isinstance(wine_type, Sequence):
                wine_type = (wine_type,)
            wine_type = tuple((wt.value if isinstance(wt, WineType) else wt for wt in wine_type))
            if len(wine_type) > 0:
                query = query.where(func.json_value(w.c.category, "$.co2").in_(wine_type))

        if grape_variety is not None:
            query = query.join(wg, wg.c.wine_entity == we.c.id) \
                .group_by(we.c.id) \
                .having(func.max(wg.c.percent) > 85 if grape_variety == GrapeVariety.SINGLE else func.max(wg.c.percent) <= 85)

        if event_year is not None:
            subquery = select(
                awe
            ).select_from(awe) \
                .join(a, a.c.id == awe.c.award_id) \
                .join(e, e.c.id == a.c.event_id) \
                .where(awe.c.wine_entity_id == we.c.id)
            subquery = apply_range_filter(subquery, e.c.year, event_year)
            query = query.where(subquery.exists())

            if gwmr is not None:
                subquery = select(
                    wgwmr
                ).select_from(wgwmr) \
                    .where(
                    wgwmr.c.wine_entity_id == we.c.id
                    )
                subquery = apply_range_filter(subquery, (wgwmr.c.year_from, wgwmr.c.year_to), event_year)
                subquery = apply_range_filter(subquery, wgwmr.c.rating, gwmr)
                query = query.where(subquery.exists())

        elif gwmr is not None:
            query = apply_range_filter(query, we.c.gwmr, gwmr)

        return query

    def build_top_wines_url(
            self,
            countries_ids: List[int] | Tuple[int] | int | None = None,
            grapes_ids: List[int] | Tuple[int] | int | None = None,
            wine_color: Tuple[WineColor, ...] | WineColor = None,
            wine_type: Tuple[WineType, ...] | WineType = None,
            grape_variety: GrapeVariety = None,
            rating_type: GWMRUrlRatingType = None,
            event_year: Tuple[int, int] = None,
            vintage: List[int] | Tuple[int] | int | None = None,
    ) -> str:
        """
        Build the URL to the top wines on GWMR website.

        :param countries_ids: The list of countries IDs.
        :param grapes_ids: The list of grapes IDs.
        :param wine_color: The wine color.
        :param wine_type: The wine type.
        :param grape_variety: The grape variety.
        :param rating_type: The rating type.
        :param event_year: The event year.
        :param vintage: Wine vintage

        :return: The URL.
        """
        url_args = {
            "mode": "expert",
        }

        if countries_ids is not None:
            url_args["country[]"] = countries_ids

        if grapes_ids is not None:
            url_args["grape[]"] = grapes_ids

        if wine_color is not None:
            url_args["color[]"] = []
            if isinstance(wine_color, WineColor):
                url_args["color[]"].append(wine_color.value)
            else:
                for color in wine_color:
                    url_args["color[]"].append(color.value)

        if wine_type is not None:
            url_args["co2[]"] = []
            if isinstance(wine_type, WineType):
                url_args["co2[]"].append(wine_type.value)
            else:
                for t in wine_type:
                    url_args["co2[]"].append(t.value)

        if grape_variety is not None:
            if grape_variety == GrapeVariety.SINGLE:
                url_args["grapes_mix[]"] = ["single_grape"]
            elif grape_variety == GrapeVariety.BLEND:
                url_args["grapes_mix[]"] = ["blends"]
            else:
                raise ValueError("Invalid grape variety.")

        if rating_type == GWMRUrlRatingType.BY_GWMR:
            pass
        elif rating_type == GWMRUrlRatingType.BY_MEDALS:
            url_args["sort"] = "awards"
        else:
            raise ValueError("Invalid rating type.")

        if event_year is not None:
            url_args["competition_year[]"] = []
            for year in range(event_year[0], event_year[1] + 1):
                url_args["competition_year[]"].append(year)

        if vintage is not None:
            url_args["vintage[]"] = vintage

        query = urlencode(url_args, doseq=True)

        return urlunsplit(["https", settings.GWMR_FINDER_DOMAIN, "/wines/", query, None])

    def __init__(self, request: HttpRequest):
        graphics_path = os.path.join(settings.MEDIA_ROOT, "graphics")
        if not os.path.exists(graphics_path):
            os.makedirs(graphics_path, mode=0o755)
        self.database = Database()
        self.request = request
        self.request_values = request.GET

        self.form: Form | None = None  # Form instance.

        mpl.use('Agg')

    def build_continent_case(self, country_field: Column) -> Case:
        """
        Returns a case statement that returns the continent of the given country.
        """
        return case(*[(country_field.in_(self.CONTINENTS[continent]), continent) for continent in self.CONTINENTS], else_=None)

    def format_file_name(self, *args: str) -> str:
        """
        Formats file name to be used as a file name using SHA1 hash.

        :param args: Logical parts of the file name.

        :return: Formatted file name.
        """
        return sha1("_".join(args).encode()).hexdigest()

    def render_template(self, template_name: str, **kwargs):
        """
        A helper methods which emulates Flask's render_template function.

        See: https://flask.palletsprojects.com/en/2.2.x/api/#flask.render_template

        TODO: Rename or completely remove this method.
        """
        return render_to_string(template_name, kwargs, self.request)

    @property
    @abstractmethod
    def title(self) -> str:
        """
        Returns the title of the report.

        :return: The title of the report.
        """
        pass

    @abstractmethod
    def render(self) -> str:
        """
        Renders the report.

        :return: HTML code of the report.
        """
        pass

    def get_form(self, *args, **kwargs) -> Form:
        """
        Returns the form instance.

        :param args: Arguments to pass to the form constructor.
        :param kwargs: Kwarg arguments to pass to the form constructor.

        :return: Form instance.
        """
        self.form = DefaultReportForm(*args, **kwargs)
        return self.form

    @property
    @abstractmethod
    def weight(self) -> int:
        """
        Returns the weight of the report for ordering.

        :return: Weight of the report.
        """
        pass

    @property
    def year_from(self):
        if self.form is not None:
            year_from = self.form.cleaned_data.get("year_from")
        else:
            year_from = self.request.POST.get("year_from") or self.request.GET.get("year_from")
        if year_from is not None:
            return int(year_from)
        return None

    @property
    def year_to(self):
        if self.form is not None:
            year_to = self.form.cleaned_data.get("year_to")
        else:
            year_to = self.request.POST.get("year_to") or self.request.GET.get("year_to")
        if year_to is not None:
            return int(year_to)
        return None


class Section:
    def __init__(self, name, weight, chapter):
        self.name = name
        self.weight = weight
        self.chapter = chapter
