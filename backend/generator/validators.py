from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from generator.utils.report import SubsectionsBySections


def validate_even(value):
    if value % 2 != 0:
        raise ValidationError(
            _('%(value)s is not an even number'),
            params={'value': value},
        )

def validate_section(name: str):
    SubsectionsBySections.get_subsections_by_sections()
    SubsectionsBySections.get_sections_by_chapters()

    if name not in SubsectionsBySections.sections_by_chapters:
        raise ValidationError(
            _('Section "%(name)s" does not exist.'),
            params={ 'name': name },
        )
