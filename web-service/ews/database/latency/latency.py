"""
    Class Model for `Latency` Collections
"""

from mongoengine import Document, StringField, IntField, FloatField, DateTimeField
import datetime


# TODO: Add `drone_id` field to tag the image source
class LatencyModel(Document):
    meta = {'collection': 'Latency'}
    frame_id = IntField(required=False)  # bugfix: for Sorter latency, there is no `frame_id`!!
    category = StringField(required=True)
    algorithm = StringField(required=True)
    section = StringField(required=True)
    latency = FloatField(required=True)
    node_id = StringField(default="-")
    node_name = StringField(default="-")
    created_at = DateTimeField(default=datetime.datetime.now)
