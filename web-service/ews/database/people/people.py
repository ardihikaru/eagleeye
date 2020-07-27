"""
    Class Model for `People` Collections
"""

from mongoengine import Document, StringField, DateTimeField
import datetime


class PeopleModel(Document):
    meta = {'collection': 'People'}
    name = StringField(required=True, unique=True)
    ssid = StringField(required=True, unique=True)
    description = StringField()
    sync_datetime = DateTimeField(required=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    def update(self, **kwargs):
        kwargs["updated_at"] = datetime.datetime.now()
        return super(PeopleModel, self).update(**kwargs)
