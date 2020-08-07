"""
    Class Model for `Latency` Collections
"""

from mongoengine import Document, StringField, IntField, FloatField
import datetime


# TODO: Add `drone_id` field to tag the image source
class LatencyModel(Document):
    meta = {'collection': 'Latency'}
    frame_id = IntField(required=True)
    category = StringField(required=True)
    algorithm = StringField(required=True)
    section = StringField(required=True)
    latency = FloatField(required=True)
    node_id = StringField(default="-")
    node_name = StringField(default="-")
