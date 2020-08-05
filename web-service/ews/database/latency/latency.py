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
