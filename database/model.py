from peewee import Model, IntegerField, CharField, BooleanField, FloatField, ForeignKeyField, SqliteDatabase
import json

database = SqliteDatabase('pgsparklite.db')


class BaseModel(Model):
    id = IntegerField(primary_key=True, unique=True)

    class Meta:
        database = database


class PedalParameter(BaseModel):
    effect_name = CharField()
    on_off = BooleanField()
    _parameters = CharField()

    def parameters(self):
        return json.loads(self._parameters)

    def store_parameters(self, parameters):
        self._parameters = json.dumps(parameters)

class PedalPreset(BaseModel):
    name = CharField()
    pedal_parameter = ForeignKeyField(PedalParameter)
    effect_name = CharField(index=True)


class ChainPreset(BaseModel):
    name = CharField()
    system_preset_id = IntegerField(null=True, unique=True)
    gate_pedal_parameter = ForeignKeyField(PedalParameter)
    comp_pedal_parameter = ForeignKeyField(PedalParameter)
    drive_pedal_parameter = ForeignKeyField(PedalParameter)
    amp_pedal_parameter = ForeignKeyField(PedalParameter)
    mod_pedal_parameter = ForeignKeyField(PedalParameter)
    delay_pedal_parameter = ForeignKeyField(PedalParameter)
    reverb_pedal_parameter = ForeignKeyField(PedalParameter)


# Create and initialise the database if necessary
database.create_tables([PedalParameter, PedalPreset, ChainPreset])
