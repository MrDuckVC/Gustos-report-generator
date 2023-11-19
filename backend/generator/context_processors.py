from generator.utils.report import SubsectionsBySections


def sections(request):
    # TODO: Use django.core.cache.
    
    SubsectionsBySections.get_subsections_by_sections()
    SubsectionsBySections.get_sections_by_chapters()

    return {
        "sections": SubsectionsBySections.sections_by_chapters.items(),
    }
