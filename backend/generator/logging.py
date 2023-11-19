import logging


class TaskLogHandler(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self)

    def emit(self, record):
        if record.name == "generator.tasks":
            from generator.models import TaskLogEntry

            log_entry = TaskLogEntry()
            log_entry.task_id = record.task_id
            log_entry.message = record.message
            log_entry.level = record.levelno
            log_entry.save()
