import threading
import base64
from abc import ABC
from io import BytesIO
from typing import IO

import numpy as np
from django.http import HttpRequest
from matplotlib import pyplot as plt
from sqlalchemy import select
from sqlalchemy.sql import func

from generator.forms import SectionWineryReportForm
from generator.models import Task, TaskStatus
from generator.reports.report import Report
from generator.tasks import generate_personal_report
from generator.utils.formatting import format_entity_name
from gustos.models import (
    wine, wine_entity,
    taxonomy_term, award,
    award_wine_entity,
    competition, event, winery,
)
from main.utils.serialization import serialize_request

# Global lock for matplotlib.
# Charts are rendered in separate threads, but 'pyplot' is static class, so we need to lock the rendering process.
pyplot_lock = threading.Lock()


class WineryReport(Report, ABC):
    def higher_than_the_average(self, a, b):
        return (a - b) * 100 / b

    def lower_than_the_average(self, a, b):
        return (b - a) * 100 / b

    def build_bars(self, a, b, winery, country_or_region, output: IO):
        with pyplot_lock:
            x = np.array([format_entity_name(winery), country_or_region])
            y = np.array([a, b])

            plt.bar(x, y, color=("steelblue", "silver"))
            plt.savefig(output, format="png")
            plt.close()

    def build_bars_base64(self, a, b, winery, country_or_region):
        buffer = BytesIO()
        self.build_bars(a, b, winery, country_or_region, buffer)
        return f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode('utf-8')}"

    def build_scatter(self, x, y, name_x, name_y, name_file):
        with pyplot_lock:
            x = np.array(x)
            y = np.array(y)
            plt.xlabel(name_x)
            plt.ylabel(name_y)
            plt.scatter(x, y)
            # Calculate equation for trendline.
            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)

            # Add trendline to plot.
            plt.plot(x, p(x))
            plt.savefig(self.get_graphic_path(name_file))
            plt.close()

    def get_winery_country_id(self, winery_id: str):
        """
        Return: country, winery_country.
        """
        with self.database.connect() as connection:
            query = select(winery.c.country, taxonomy_term.c.name) \
                .select_from(winery) \
                    .join(taxonomy_term, winery.c.country == taxonomy_term.c.tid) \
                    .where(winery.c.id == winery_id)
            result = connection.execute(query)

        country = result.fetchone()
        return country

    def determ_gr_color(self, limit: float):
        """
        Returns the color for the selected piece of the chart
        """
        if limit <= 20:
            return "limegreen"
        elif limit <= 50:
            return "darkturquoise"
        return "r"

    def build_pie_chart(self, x: int, color: str, output: IO):
        """
        - x - count
        - color - color for x ring sector
        """
        with pyplot_lock:
            # Dependencies
            if x < 1:
                x = 1
            vals = [100 - x, x]
            labels = ["", ""]

            # Build chart
            fig, ax = plt.subplots(figsize=(3, 3))
            fig.subplots_adjust(left=-0.1, bottom=-0.1, right=1.1, top=1.1, wspace=2, hspace=2)
            plt.text(0, 0, f"{x}%", horizontalalignment='center', verticalalignment='center', fontsize=30, color=color)
            ax.pie(vals, labels=labels, wedgeprops=dict(width=0.35), colors=("#7e1538", color))

            # Save chart
            plt.savefig(output, format="png")
            plt.close()

    def build_pie_chart_base64(self, x: int, color: str):
        buffer = BytesIO()
        self.build_pie_chart(x, color, buffer)
        return f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode('utf-8')}"

    def calc_percentages(self, total_x, x):
        """
        What percentage is one number of another number.
        """
        return round((int(x) / int(total_x)) * 100)

    def get_total_number_of_medals(self, winery_id: str, year1: str, year2: str):
        with self.database.connect() as connection:
            query = select(func.count(award.c.value)) \
                .select_from(award) \
                    .join(event, award.c.event_id == event.c.id) \
                    .join(competition, event.c.competition_id == competition.c.id) \
                    .join(award_wine_entity, award.c.id == award_wine_entity.c.award_id) \
                    .join(wine_entity, wine_entity.c.id == award_wine_entity.c.wine_entity_id) \
                    .join(wine, wine.c.id == wine_entity.c.wine) \
                    .join(winery, winery.c.id == wine.c.winery) \
                    .where(
                        winery.c.id == winery_id,
                        event.c.year.between(year1, year2)
                    )
            result = connection.execute(query)
        total_number_of_medals, = result.fetchone()
        return total_number_of_medals

    def __init__(self, request: HttpRequest):
        super().__init__(request)
        self.form = None

    def get_form(self, *args, **kwargs):
        self.form = SectionWineryReportForm(*args, **kwargs)
        return self.form

    def enqueue_report_generation(self):
        task = Task()
        task.request = serialize_request(self.request)
        task.winery = self.winery_id
        task.year_from = self.year_from
        task.year_to = self.year_to
        task.status = TaskStatus.PENDING
        task.clean()
        task.save()
        generate_personal_report.delay(task.id)
        return task

    @property
    def winery_id(self):
        if self.form is not None:
            winery_id = self.form.cleaned_data.get("winery")
        else:
            winery_id = self.request.POST.get("winery") or self.request.GET.get("winery")
        if winery_id is not None:
            return int(winery_id)
        return None
