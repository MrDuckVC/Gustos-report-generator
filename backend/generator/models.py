import logging
import uuid
from collections import defaultdict
from datetime import datetime

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext as _
from django_mysql.models import EnumField

from gustos.models import Winery
from main.settings import Database


class TaskStatus(models.TextChoices):
    PENDING = "PENDING", _("Pending")
    IN_PROGRESS = "IN_PROGRESS", _("In progress")
    FINISHED = "FINISHED", _("Finished")
    FAILED = "FAILED", _("Failed")


class Task(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    celery_id = models.UUIDField(editable=False, null=True)
    request = models.JSONField()
    winery = models.PositiveIntegerField(null=False, blank=False)
    winery_name = models.CharField(null=False, blank=False, max_length=255)
    year_from = models.PositiveSmallIntegerField(null=False, blank=False, validators=[MinValueValidator(2000), MaxValueValidator(datetime.now().year)])
    year_to = models.PositiveSmallIntegerField(null=False, blank=False, validators=[MinValueValidator(2000), MaxValueValidator(datetime.now().year)])
    status = EnumField(choices=TaskStatus.choices, null=False, blank=False, default=TaskStatus.PENDING)
    current = models.PositiveIntegerField(null=False, blank=False, default=0, editable=False)
    total = models.PositiveIntegerField(null=False, blank=False, default=0, editable=False)
    file = models.FileField(upload_to="pdf/%Y/%m/%d/", null=True, blank=True)
    created = models.DateTimeField(null=False, blank=False, auto_now_add=True)
    updated = models.DateTimeField(null=False, blank=False, auto_now=True)

    class Meta:
        ordering = ("-updated", )

    def clean(self):
        errors = defaultdict(list)

        try:
            self.winery_name = Winery.objects.using(Database.GUSTOS.value).values_list("name", flat=True).get(id=self.winery)
        except Winery.DoesNotExist:
            errors["winery"].append(_('Winery with identifier "%(id)s" does not exist.') % {"id": self.winery})

        if self.year_to and self.year_to and self.year_to < self.year_from:
            errors["year_from"].append(_("Start of the period cannot be greater than end of one."))

        if len(errors) > 0:
            raise ValidationError(errors)


class TaskLogEntryLevel(models.IntegerChoices):
    CRITICAL = logging.CRITICAL, _("Critical")
    ERROR = logging.ERROR, _("Error")
    WARNING = logging.WARNING, _("Warning")
    INFO = logging.INFO, _("Info")
    DEBUG = logging.DEBUG, _("Debug")
    NOTSET = logging.NOTSET, _("Notset")

    __empty__ = _("(Unknown)")


class TaskLogEntry(models.Model):
    task = models.ForeignKey(Task, null=False, blank=False, on_delete=models.CASCADE, editable=False)
    message = models.TextField(max_length=2048, null=False, blank=False, editable=False)
    level = models.IntegerField(choices=TaskLogEntryLevel.choices, null=False, blank=False, editable=False)
    created = models.DateTimeField(null=False, blank=False, auto_now_add=True, editable=False)

    class Meta:
        ordering = ("created", )