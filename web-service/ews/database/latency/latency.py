"""
    Class Model for `Latency` Collections
"""

from mongoengine import Document, StringField, DateTimeField, FloatField
import datetime


class LatencyModel(Document):
    meta = {'collection': 'Latency'}
    category = StringField(required=True)
    algorithm = StringField(required=True)
    section = StringField(required=True)
    latency = FloatField(required=True)
    timestamp = FloatField(required=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    #  it overrides the usage of the original update function
    def update(self, **kwargs):
        kwargs["updated_at"] = datetime.datetime.now()  # forcefully update this `updated_at` Field
        return super(LatencyModel, self).update(**kwargs)
