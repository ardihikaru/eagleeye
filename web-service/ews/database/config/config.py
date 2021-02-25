"""
    Class Model for `Configs` Collections
"""

from mongoengine import Document, StringField, DateTimeField, BooleanField, EmbeddedDocument, EmbeddedDocumentField
import datetime


class Extras(EmbeddedDocument):
    selector = StringField(default=None)  # used by ZENOH


class ConfigModel(Document):
    meta = {'collection': 'Configs'}
    uri = StringField(required=True, unique=True)
    algorithm = StringField(required=True)
    scalable = BooleanField(required=True)
    stream = StringField(required=True)

    # Source: https://stackoverflow.com/questions/17872836/embedded-documents-issue-with-mongoengine
    extras = EmbeddedDocumentField(Extras, default=Extras)

    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    #  it overrides the usage of the original update function
    def update(self, **kwargs):
        kwargs["updated_at"] = datetime.datetime.now()  # forcefully update this `updated_at` Field
        return super(ConfigModel, self).update(**kwargs)
