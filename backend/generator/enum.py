from enum import Enum


class WineType(Enum):
    SPARKLING = 1360
    STILL = 1358
    PEARL = 1359


class WineColor(Enum):
    WHITE = 1170
    ROSE = 1171
    RED = 1169


class GrapeVariety(Enum):
    BLEND = True
    SINGLE = False


class Continent(Enum):
    AFRICA = 1
    ASIA = 2
    EUROPE = 3
    NORTH_AMERICA = 4
    PACIFIC = 5
    SOUTH_AMERICA = 6


class AwardValue(Enum):
    GRAND_GOLD = "GRAND"
    GOLD = "GOLD"
    SILVER = "SILVER"
    BRONZE = "BRONZE"


class GWMRUrlRatingType(Enum):
    BY_GWMR = "by_gwmr"
    BY_MEDALS = "by_medals"


class CompetitionRegion(Enum):
    MULTIPLE = "MULTIPLE"
    NORTH_AMERICA = "NORTH_AMERICA"
    AFRICA = "AFRICA"
    SOUTH_AMERICA = "SOUTH_AMERICA"
    WEST_EUROPE = "WEST_EUROPE"
    EAST_EUROPE = "EAST_EUROPE"
    ASIA = "ASIA"
    AUSTRALIA = "AUSTRALIA"
    CIS = "CIS"  # There are no competitions with region "CIS" in actual database (and shouldn`t have it).

    def get_continent(self) -> Continent | None:
        match self:
            case CompetitionRegion.NORTH_AMERICA:
                return Continent.NORTH_AMERICA
            case CompetitionRegion.AFRICA:
                return Continent.AFRICA
            case CompetitionRegion.SOUTH_AMERICA:
                return Continent.SOUTH_AMERICA
            case CompetitionRegion.WEST_EUROPE | CompetitionRegion.EAST_EUROPE:
                return Continent.EUROPE
            case CompetitionRegion.ASIA:
                return Continent.ASIA
            case CompetitionRegion.AUSTRALIA:
                return Continent.PACIFIC
            case CompetitionRegion.CIS, CompetitionRegion.MULTIPLE:
                return None


class BeverageType:
    BEER = 1570
    BRANDY_DIVIN_WEINBRAND = 1428
    CHACHA = 1437
    GRAPE_MARC_SPIRIT = 1433
    GRAPE_SPIRIT = 1431
    GRAPPA = 1438
    LIQUOR = 1435
    MISTELLE = 1429
    OTHER = 1440
    OTHER_SPIRITUOUS_BEVERAGE = 1427
    RAISIN_SPIRIT = 1432
    TINCTURE = 1439
    VITIVINICULTORAL_ORIGIN_PIRITUOUS_BEVERAGE = 1426
    VODKA = 1436
    WINE = 1425
    WINE_LEES_SPIRIT = 1434
    WINE_SPIRIT = 1430
