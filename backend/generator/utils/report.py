import inspect
import os
from importlib.machinery import SourceFileLoader
from typing import IO

import pdfkit
from bs4 import BeautifulSoup
from django.conf import settings
from django.http import HttpRequest
from django.template.loader import render_to_string

import generator
from generator.reports.report import Report, Section


def generating_pdf_report(html, output: IO, **kwargs):

    html = render_to_string("pdf.html", {
        "result_data": html,
        ** kwargs,
    })

    document = BeautifulSoup(html, "html.parser")

    # Replaces URLs to static and media files by its absolute path.
    for element in document.head.findAll(lambda e: e.name == "link" and e.has_attr("href")):
        if element["href"].startswith(settings.STATIC_URL):
            element["href"] = os.path.join(settings.STATIC_ROOT, element["href"][len(settings.STATIC_URL):])
        elif element["href"].startswith(settings.MEDIA_URL):
            element["href"] = os.path.join(settings.MEDIA_ROOT, element["href"][len(settings.MEDIA_URL):])
    for element in document.findAll(lambda e: e.has_attr("src")):
        if element["src"].startswith(settings.STATIC_URL):
            element["src"] = os.path.join(settings.STATIC_ROOT, element["src"][len(settings.STATIC_URL):])
        elif element["src"].startswith(settings.MEDIA_URL):
            element["src"] = os.path.join(settings.MEDIA_ROOT, element["src"][len(settings.MEDIA_URL):])

    options = {
        'page-size': 'B3',
        'margin-top': '0',
        'margin-right': '0',
        'margin-bottom': '0',
        'margin-left': '0',
        'encoding': 'UTF-8',
        'no-outline': None,
        'enable-local-file-access': None,
        'load-error-handling': 'ignore',
        'print-media-type': None,
    }

    output.write(pdfkit.PDFKit(str(document), "string", options=options).to_pdf())


def get_section(section: str):
    """
    Get report object of section by its names.
    :param section: name of section
    :return: object
    """
    sections_dir = os.path.dirname(inspect.getfile(generator.reports))
    module_path = os.path.join(sections_dir, section, "main.py")
    module = SourceFileLoader(section, module_path).load_module()

    for name in dir(module):
        if isinstance(getattr(module, name), Section):
            try:
                return getattr(module, name)
            except TypeError:
                continue


def get_report(request: HttpRequest, section: str, subsection: str, **kwargs):
    """
    Get report object of subsection by its section and subsection names.

    :param request: request object of Django framework
    :param section: name of section
    :param subsection: name of subsection
    :param kwargs: additional arguments

    :return: report object
    """
    sections_dir = os.path.dirname(inspect.getfile(generator.reports))
    module_path = os.path.join(sections_dir, section, subsection, "main.py")
    module = SourceFileLoader(subsection, module_path).load_module()

    # Get all classes from module.
    classes = [cls_name for cls_name, cls_obj in inspect.getmembers(module) if inspect.isclass(cls_obj)]

    # Find class with subclass Reports.
    for name in classes:
        if issubclass(getattr(module, name), Report):
            try:
                return getattr(module, name)(request, **kwargs)
            except TypeError:
                continue


class SubsectionsBySections:
    got_subsections_by_sections = False
    subsections_by_sections = {}
    got_sections_by_chapters = False
    sections_by_chapters = {}

    @staticmethod
    def get_sections_by_chapters():
        sections_list = SubsectionsBySections.subsections_by_sections.keys()  # Default sections list to be shown.
        SubsectionsBySections.sections_by_chapters = {}
        for section in sections_list:
            section_info = get_section(section)

            if not SubsectionsBySections.sections_by_chapters.get(section_info.chapter):
                SubsectionsBySections.sections_by_chapters[section_info.chapter] = []

            SubsectionsBySections.sections_by_chapters[section_info.chapter].append(
                {
                    "name": section_info.name,
                    "slug": section,
                    "weight": section_info.weight,
                }
            )

        for chapter in SubsectionsBySections.sections_by_chapters:
            SubsectionsBySections.sections_by_chapters[chapter] = sorted(SubsectionsBySections.sections_by_chapters[chapter], key=lambda d: d["weight"])

        SubsectionsBySections.got_sections_by_chapters = True

    @staticmethod
    def get_subsections_by_sections():
        sections_dir = os.path.dirname(inspect.getfile(generator.reports))

        # Get sections list form sections_dir.
        sections_list = [name for name in os.listdir(sections_dir) if os.path.isdir(os.path.join(sections_dir, name))]
        sections_list.remove("__pycache__")

        sections_by_weight = {}
        for section in sections_list:
            section_info = get_section(section)
            sections_by_weight[section] = section_info.weight

        sections_list = [k for k, v in sorted(sections_by_weight.items(), key=lambda item: item[1])]

        for section in sections_list:
            subsections_dir = os.path.join(sections_dir, section)

            # Get subsection list form subsections_dir.
            subsections_list = [name for name in os.listdir(subsections_dir) if os.path.isdir(os.path.join(subsections_dir, name))]
            subsections_list.remove("__pycache__")

            SubsectionsBySections.subsections_by_sections[section] = subsections_list

        SubsectionsBySections.got_subsections_by_sections = True
