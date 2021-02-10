from peewee import Model, IntegerField, CharField, BooleanField, FloatField, ForeignKeyField, SqliteDatabase

database = SqliteDatabase('pgsparklite.db')


class BaseModel(Model):
    id = IntegerField(primary_key=True)

    class Meta:
        database = database


class PedalParameter(BaseModel):
    effect_name = CharField()
    on_off = BooleanField()
    p1_value = FloatField()
    p2_value = FloatField()
    p3_value = FloatField()
    p4_value = FloatField()
    p5_value = FloatField()
    p6_value = FloatField()


class PedalPreset(BaseModel):
    name = CharField()
    pedal_parameter_id = ForeignKeyField(PedalParameter)
    effect_type = CharField()


class ChainPreset(BaseModel):
    name = CharField()
    gate_pedal_parameter_id = ForeignKeyField(PedalParameter)
    drive_pedal_parameter_id = ForeignKeyField(PedalParameter)
    amp_pedal_parameter_id = ForeignKeyField(PedalParameter)
    mod_pedal_parameter_id = ForeignKeyField(PedalParameter)
    delay_pedal_parameter_id = ForeignKeyField(PedalParameter)
    reverb_pedal_parameter_id = ForeignKeyField(PedalParameter)


# Create and initialise the database if necessary
database.create_tables([PedalParameter, PedalPreset, ChainPreset])
