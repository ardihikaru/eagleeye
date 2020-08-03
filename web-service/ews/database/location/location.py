"""
    Class Model for `Locations` Collections
"""

from mongoengine import Document, StringField, DateTimeField, FloatField
import datetime


class LocationModel(Document):
    meta = {'collection': 'Locations'}
    name = StringField(required=True)
    long = FloatField(required=True)
    lat = FloatField(required=True)
    alt = FloatField(required=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    #  it overrides the usage of the original update function
    def update(self, **kwargs):
        kwargs["updated_at"] = datetime.datetime.now()  # forcefully update this `updated_at` Field
        return super(LocationModel, self).update(**kwargs)
