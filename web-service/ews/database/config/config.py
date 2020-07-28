"""
    Class Model for `Configs` Collections
"""

from mongoengine import Document, StringField, DateTimeField, BooleanField
import datetime


class ConfigModel(Document):
    meta = {'collection': 'Configs'}
    uri = StringField(required=True, unique=True)
    algorithm = StringField(required=True)
    scalable = BooleanField(required=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    #  it overrides the usage of the original update function
    def update(self, **kwargs):
        kwargs["updated_at"] = datetime.datetime.now()  # forcefully update this `updated_at` Field
        return super(ConfigModel, self).update(**kwargs)
