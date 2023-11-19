from django.db import models
from sqlalchemy import (Boolean, Column, Enum, ForeignKey, Integer, MetaData,
                        Numeric, SmallInteger, String, Table)

metadata_obj = MetaData()

taxonomy_term = Table(
    'taxonomy_term',
    metadata_obj,
    Column('tid', Integer, primary_key=True),
    Column('vid', Integer),
    Column('name', String(255)),
    Column('description', String(255)),
    Column('format', String(255)),
    Column('weight', Integer),
    Column('language', String(12)),
    Column('i18n_tsid', Integer),
)


# > DESCRIBE file_managed;
# +-----------+---------------------+------+-----+---------+----------------+
# | Field     | Type                | Null | Key | Default | Extra          |
# +-----------+---------------------+------+-----+---------+----------------+
# | fid       | int(10) unsigned    | NO   | PRI | NULL    | auto_increment |
# | uid       | int(10) unsigned    | NO   | MUL | 0       |                |
# | filename  | varchar(255)        | NO   |     |         |                |
# | uri       | varchar(255)        | NO   | UNI |         |                |
# | filemime  | varchar(255)        | NO   |     |         |                |
# | filesize  | bigint(20) unsigned | NO   |     | 0       |                |
# | status    | tinyint(4)          | NO   | MUL | 0       |                |
# | timestamp | int(10) unsigned    | NO   | MUL | 0       |                |
# +-----------+---------------------+------+-----+---------+----------------+

file_managed = Table(
    'file_managed',
    metadata_obj,
    Column('fid', Integer, primary_key=True),
    Column('uid', Integer, nullable=False),
    Column('filename', String(255), nullable=False),
    Column('uri', String(255), nullable=False, unique=True),
    Column('filemime', String(255), nullable=False),
    Column('filesize', Integer, nullable=False),
    Column('status', Boolean, nullable=False),
    Column('timestamp', Integer, nullable=False),
)

winery = Table(
    "winery",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("uid", Integer, nullable=False),
    Column("name", String(255), nullable=False),
    Column("country", Integer, ForeignKey(taxonomy_term.c.tid.name)),
    Column("region", String(255)),
    Column("phone", String(32), nullable=False),
    Column("description", String(255)),
    Column("logo", Integer, ForeignKey(file_managed.c.fid.name)),
    Column("created", Integer, nullable=False),
    Column("updated", Integer, nullable=False),
    Column("website", String(1024)),
    Column("slug", String(255), unique=True),
)

wine = Table(
    "wine",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", String(255), nullable=False),
    Column("winery", Integer, ForeignKey(winery.c.id.name), nullable=False),
    Column("country", Integer, ForeignKey(taxonomy_term.c.tid.name), nullable=False),
    Column("series", Integer, ForeignKey(taxonomy_term.c.tid.name)),
    Column("include_series", Boolean),
    Column("category", String(255)),
    Column("created", Integer, nullable=False),
    Column("updated", Integer, nullable=False),
    Column("color", Integer, ForeignKey(taxonomy_term.c.tid.name)),
    Column("beverage_type_secondary", Integer, ForeignKey(taxonomy_term.c.tid.name)),
)

wine_entity = Table(
    "wine_entity",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("wine", Integer, ForeignKey(wine.c.id.name), nullable=False),
    Column("photo", Integer, ForeignKey(file_managed.c.fid.name)),
    Column("is_igp", Boolean),
    Column("stage_of_production", Integer, ForeignKey(taxonomy_term.c.tid.name)),
    Column("prod_volume", Numeric(10, 2)),
    Column("prod_unit", Integer, ForeignKey(taxonomy_term.c.tid.name)),
    Column("alcohol", Numeric(10, 2)),
    Column("sugar", Numeric(10, 2)),
    Column("vintage", Integer, nullable=False),
    Column("created", Integer, nullable=False),
    Column("updated", Integer, nullable=False),
    Column("region", Integer, ForeignKey(taxonomy_term.c.tid.name)),
    Column("include_region", Boolean),
    Column("gwmr", Numeric(14, 10)),
)

competition = Table(
    "competition",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", String(255), nullable=False),
    Column("description", String(255)),
    Column("region", Enum("MULTIPLE", "NORTH_AMERICA", "AFRICA", "SOUTH_AMERICA", "WEST_EUROPE", "EAST_EUROPE", "ASIA", "AUSTRALIA", "CIS"), nullable=False),
    Column("google_page_rating", Numeric(10, 2), nullable=False),
    Column("correction_factor", Numeric(10, 2), nullable=False),
    Column("rating", Numeric(10, 2), nullable=False),
    Column("created", Integer, nullable=False),
    Column("updated", Integer, nullable=False),
    Column("logo_id", Integer, ForeignKey(file_managed.c.fid.name)),
)

event = Table(
    "event",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("country_id", Integer, ForeignKey(taxonomy_term.c.tid.name)),
    Column("competition_id", Integer, ForeignKey(competition.c.id.name), nullable=False),
    Column("year", SmallInteger, nullable=False),
    Column("wine_count", SmallInteger, nullable=False),
    Column("medal_count", SmallInteger, nullable=False),
    Column("created", Integer, nullable=False),
    Column("updated", Integer, nullable=False),
)

award = Table(
    "award",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", String(255), nullable=False),
    Column("description", String(255)),
    Column("event_id", Integer, ForeignKey(event.c.id.name), nullable=False),
    Column("value", Enum("GRAND", "GOLD", "SILVER", "BRONZE"), nullable=False),
    Column("weight", Integer, nullable=False),
    Column("min_rating", Numeric(5, 2), nullable=False),
    Column("max_rating", Numeric(5, 2), nullable=False),
    Column("photo_id", Integer, ForeignKey(file_managed.c.fid.name)),
    Column("created", Integer, nullable=False),
    Column("updated", Integer, nullable=False),
)

award_wine_entity = Table(
    "award_wine_entity",
    metadata_obj,
    Column("award_id", Integer, ForeignKey(award.c.id.name), nullable=False),
    Column("wine_entity_id", Integer, ForeignKey(wine_entity.c.id.name), nullable=False),
    Column("exact_score", Numeric(5, 2)),
)

wine_grapes = Table(
    "wine_grapes",
    metadata_obj,
    Column("wine_entity", Integer, ForeignKey(wine_entity.c.id.name), nullable=False),
    Column("grape", Integer, ForeignKey(taxonomy_term.c.tid.name), nullable=False),
    Column("percent", Integer, nullable=False),
    Column("wine", Integer, ForeignKey(wine.c.id.name), nullable=False),
)

wine_gwmr = Table(
    "wine_gwmr",
    metadata_obj,
    Column("wine_entity_id", Integer, ForeignKey(wine_entity.c.id.name), nullable=False),
    Column("year_from", Integer, nullable=False),
    Column("year_to", Integer, nullable=False),
    Column("rating", Numeric(14, 10)),
)


# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.


class FileManaged(models.Model):
    fid = models.AutoField(primary_key=True)
    uid = models.PositiveIntegerField()
    filename = models.CharField(max_length=255)
    uri = models.CharField(unique=True, max_length=255, db_collation='utf8mb4_bin')
    filemime = models.CharField(max_length=255, db_collation='utf8mb4_bin')
    filesize = models.PositiveBigIntegerField()
    status = models.IntegerField()
    timestamp = models.PositiveIntegerField()

    class Meta:
        managed = False
        db_table = 'file_managed'


class Wine(models.Model):
    name = models.CharField(max_length=255)
    winery = models.PositiveIntegerField()
    country = models.PositiveIntegerField()
    series = models.PositiveIntegerField(blank=True, null=True)
    include_series = models.IntegerField(blank=True, null=True)
    category = models.TextField(db_collation='utf8mb4_bin', blank=True, null=True)
    created = models.PositiveIntegerField()
    updated = models.PositiveIntegerField()
    color = models.PositiveIntegerField(blank=True, null=True)
    beverage_type_secondary = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'wine'


class WineEntity(models.Model):
    wine = models.PositiveIntegerField()
    photo = models.PositiveIntegerField(blank=True, null=True)
    is_igp = models.IntegerField(blank=True, null=True)
    stage_of_production = models.PositiveIntegerField(blank=True, null=True)
    prod_volume = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    prod_unit = models.PositiveIntegerField(blank=True, null=True)
    alcohol = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sugar = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    vintage = models.PositiveIntegerField()
    created = models.PositiveIntegerField()
    updated = models.PositiveIntegerField()
    region = models.PositiveIntegerField(blank=True, null=True)
    include_region = models.IntegerField(blank=True, null=True)
    gwmr = models.DecimalField(max_digits=14, decimal_places=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'wine_entity'
        unique_together = (('wine', 'vintage'),)


class WineGrapes(models.Model):
    wine_entity = models.PositiveIntegerField()
    grape = models.PositiveIntegerField()
    percent = models.PositiveIntegerField()
    wine = models.PositiveIntegerField()

    class Meta:
        managed = False
        db_table = 'wine_grapes'
        unique_together = (('wine', 'wine_entity', 'grape'),)


class TaxonomyTerm(models.Model):
    tid = models.AutoField(primary_key=True)
    vid = models.PositiveIntegerField()
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    format = models.CharField(max_length=255, blank=True, null=True)
    weight = models.IntegerField()
    language = models.CharField(max_length=12)
    i18n_tsid = models.PositiveIntegerField()

    class Meta:
        managed = False
        db_table = 'taxonomy_term'


class Award(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    event_id = models.PositiveIntegerField()
    value = models.CharField(max_length=6)
    weight = models.IntegerField()
    min_rating = models.DecimalField(max_digits=5, decimal_places=2)
    max_rating = models.DecimalField(max_digits=5, decimal_places=2)
    photo_id = models.PositiveIntegerField(blank=True, null=True)
    created = models.IntegerField()
    updated = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'award'


class AwardWineEntity(models.Model):
    award_id = models.PositiveIntegerField()
    wine_entity_id = models.PositiveIntegerField()
    exact_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    created = models.IntegerField()
    updated = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'award_wine_entity'
        unique_together = (('award_id', 'wine_entity_id'),)


class Competition(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    region = models.CharField(max_length=13)
    google_page_rating = models.DecimalField(max_digits=10, decimal_places=2)
    correction_factor = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.DecimalField(max_digits=10, decimal_places=2)
    created = models.IntegerField()
    updated = models.IntegerField()
    logo_id = models.PositiveIntegerField(blank=True, null=True)
    website = models.CharField(max_length=1024, blank=True, null=True)
    use_parsed_page_rank = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'competition'


class Event(models.Model):
    country_id = models.PositiveIntegerField(blank=True, null=True)
    competition_id = models.PositiveIntegerField()
    year = models.PositiveSmallIntegerField()
    wine_count = models.PositiveSmallIntegerField()
    medal_count = models.PositiveSmallIntegerField()
    created = models.IntegerField()
    updated = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'event'
        unique_together = (('year', 'competition_id'),)


class WineGwmr(models.Model):
    wine_entity_id = models.PositiveIntegerField(primary_key=True)
    year_from = models.PositiveIntegerField()
    year_to = models.PositiveIntegerField()
    rating = models.DecimalField(max_digits=14, decimal_places=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'wine_gwmr'
        unique_together = (('wine_entity_id', 'year_from', 'year_to'),)


class Winery(models.Model):
    uid = models.PositiveIntegerField()
    name = models.CharField(max_length=255)
    country = models.PositiveIntegerField(blank=True, null=True)
    region = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=32)
    description = models.TextField(blank=True, null=True)
    logo = models.PositiveIntegerField(blank=True, null=True)
    created = models.PositiveIntegerField()
    updated = models.PositiveIntegerField()
    website = models.CharField(max_length=1024, blank=True, null=True)
    slug = models.CharField(unique=True, max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'winery'
