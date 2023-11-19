import logging
from inspect import signature
from io import BytesIO
from queue import Queue
from threading import Lock, Thread

from django.conf import settings
from django.core.files.base import ContentFile
from django.utils.translation import gettext
from pypdf import PdfMerger

from generator.exceptions import DataNotFoundException, RatingNotFoundException
from generator.models import Task, TaskStatus
from generator.utils.report import generating_pdf_report, get_report, SubsectionsBySections
from main.celery import app
from main.utils.serialization import deserialize_request


@app.task(bind=True)
def generate_personal_report(self, task_id: str):
    # TODO: May be add logger handler manually?
    logger = logging.getLogger(__name__)
    logger_extra = {
        "task_id": task_id
    }
    task = None

    try:
        task = Task.objects.get(id=task_id)
        task.celery_id = self.request.id
        task.status = TaskStatus.IN_PROGRESS
        task.save()

        logger.info(
            "The task of report generation has been started successfully.",
            extra=logger_extra
        )

        request = deserialize_request(task.request)

        SubsectionsBySections.get_subsections_by_sections()

        sections_info = {
            section: subsections for section, subsections in
                         SubsectionsBySections.subsections_by_sections.items() if section in [
                             "your_winery_profile",
                             "by_number_winery_report",
                             "by_wine_winery_report",
                             "country_region_comparison",
                         ]
        }

        reports = Queue()
        lock = Lock()

        weight = 0
        for section, subsections in sections_info.items():
            for subsection in subsections:
                report = get_report(request, section, subsection)
                reports.put((report.weight + 1000 * weight, report))
                task.total += 1
            weight += 1
        # Save "task.total".
        task.save()

        results = {}

        def worker():
            while True:
                worker_task = reports.get()
                if task is None:
                    break
                weight, report = worker_task
                try:
                    render = report.render
                    # TODO: Remove "throw_exception" parameter from all "render" methods.
                    render_sig = signature(render)
                    if len(render_sig.parameters) == 0:
                        result_data = render()
                    else:
                        result_data = render(True)

                    output = BytesIO()
                    generating_pdf_report(result_data, output)
                    results[weight] = output
                except RatingNotFoundException:
                    # TODO: Link to the report page.
                    # TODO: Storing translatable log entries in the database.
                    # TODO: Do not store rich value in console log.
                    logger.warning(
                        'An error for the "%(report)s" report occurred: %(message)s' % {
                            "report": report.title,
                            "message": f'<em>{gettext("Missing GWMR ratings for selected period. It seems that GWMR for selected period must be calculated in Gustos application first.")}</em>',
                        },
                        extra=logger_extra
                    )
                except DataNotFoundException:
                    # TODO: Link to the report page.
                    # TODO: Storing translatable log entries in the database.
                    # TODO: Do not store rich value in console log.
                    logger.warning(
                        'An error for the "%(report)s" report occurred: %(message)s' % {
                            "report": report.title,
                            "message": f'<em>{gettext("Winery is missing in result data. It seems that winery does not have awarded wines which satisfy the criteria.")}</em>',
                        },
                        extra=logger_extra
                    )
                except Exception as e:
                    # TODO: Link to the report page.
                    # TODO: Storing translatable log entries in the database.
                    # TODO: Do not store rich value in console log.
                    logger.error(
                        'An unexpected error occurred for the "%(report)s" report: %(message)s' % {
                            "report": report.title,
                            "message": str(e),
                        },
                        extra=logger_extra,
                        exc_info=e,
                        stack_info=True,
                    )
                finally:
                    with lock:
                        task.current += 1
                        task.save()
                    reports.task_done()

        thread_pool = [Thread(target=worker, daemon=True) for _ in range(settings.THREAD_POOL_SIZE)]
        for thread in thread_pool:
            thread.start()
        reports.join()
        thread_pool.clear()

        results = [r[1] for r in sorted(results.items(), key=lambda x: x[0])]

        output_filename = f"personal_report_{request.POST['winery']}_{request.POST['year_from']}_{request.POST['year_to']}.pdf"

        with BytesIO() as io:
            with PdfMerger(fileobj=io) as pdf:
                for file in results:
                    pdf.append(file)
                    file.close()
            task.file = ContentFile(io.getvalue(), name=output_filename)
            task.status = TaskStatus.FINISHED
            task.save()
            # TODO: Storing translatable log entries in the database.
            # TODO: Do not store rich value in console log.
            logger.info(
                'Successfully finished the task. The report has been generated: %(file)s' % {
                    "file": f'<a href="{task.file.url}" target="_blank">{task.file.name}</a>' if hasattr(task.file, "url") else task.file.name,
                },
                extra=logger_extra,
            )

        return task.file.name

    except Exception as e:
        # TODO: Storing translatable log entries in the database.
        # TODO: Do not store rich value in console log.
        logger.critical(
            "An unexpected error occurred: %(message)s" % {
                "message": f'<em>{str(e)}</em>',
            },
            extra=logger_extra,
            exc_info=e,
            stack_info=True,
        )
        task.status = TaskStatus.FAILED
        task.save()
        raise e
