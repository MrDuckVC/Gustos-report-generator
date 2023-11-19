from math import ceil

from generator.enum import Continent


def format_entity_name(entity_name: str):
    if entity_name is None:
        return None

    slash_position = entity_name.find("/")
    opening_bracket_position = entity_name.find("(")

    if slash_position == -1 and opening_bracket_position == -1:
        return entity_name
    elif slash_position != -1 and opening_bracket_position != -1:
        return entity_name[:min(opening_bracket_position, slash_position)].rstrip()
    else:
        return entity_name[:max(opening_bracket_position, slash_position)].rstrip()


def format_percent_rank(percent_rank: float):
    if percent_rank is None:
        return None

    percent_rank = ceil(percent_rank * 100)

    if percent_rank <= 1:
        return 1
    elif percent_rank >= 100:
        return 100
    return int(percent_rank)


def format_continent_name(continent_id: Continent | int):
    if not isinstance(continent_id, Continent):
        continent_id = Continent(continent_id)

    match continent_id:
        case Continent.AFRICA:
            return "Africa"
        case Continent.ASIA:
            return "Asia"
        case Continent.EUROPE:
            return "Europe"
        case Continent.NORTH_AMERICA:
            return "North America"
        case Continent.PACIFIC:
            return "Pacific"
        case Continent.SOUTH_AMERICA:
            return "South America"
        case _:
            return "Unknown"


def format_vintage(vintage: int):
    if vintage <= 1900:
        return "NV"
    return vintage

def format_percent(percent: float):
    if percent is None:
        return None

    return f"{round(percent, 1)}%"
