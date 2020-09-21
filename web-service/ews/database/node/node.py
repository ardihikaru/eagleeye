"""
    Class Model for `Nodes` Collections
"""

from mongoengine import Document, StringField, DateTimeField, BooleanField, IntField
import datetime


class NodeModel(Document):
    meta = {'collection': 'Nodes'}
    name = StringField(required=True, unique=True)
    channel = StringField(default="", unique=True)
    consumer = StringField()  # drone_id
    candidate_selection = BooleanField(required=True, default=True)
    persistence_validation = BooleanField(required=True, default=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    #  it overrides the usage of the original update function
    def update(self, **kwargs):
        kwargs["updated_at"] = datetime.datetime.now()  # forcefully update this `updated_at` Field
        return super(NodeModel, self).update(**kwargs)
