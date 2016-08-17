from peewee import Field, Model, CharField, BigIntegerField, DateTimeField, UUIDField, fn
from model_pckg import DATABASE

database = DATABASE


class StatusField(Field):
    db_field = 'datamining.job_status'


class BaseModel(Model):
    class Meta:
        database = database


class ProtocolJob(BaseModel):
    id = BigIntegerField(db_column='__id', primary_key=True)
    start_load = DateTimeField(db_column='__start_load', default=fn.now())
    updated = DateTimeField(db_column='__updated', null=True)
    zip_id = UUIDField(unique=True, null=False)
    zip_name = CharField(null=False)
    status = StatusField(null=False, choices=['parsing', 'failed', 'skipped', 'success'])

    class Meta:
        db_table = 'job_protocols'
        schema = 'datamining'

class ConractJob(ProtocolJob):
    start_load = DateTimeField(db_column='__start_load', default=fn.now())
    class Meta:
        db_table = 'job_contracts'
        schema = 'datamining'
