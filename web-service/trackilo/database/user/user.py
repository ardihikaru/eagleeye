"""
    Class Model for `Users` Collections
"""

from mongoengine import Document, StringField, DateTimeField, EmailField
import datetime


class UserModel(Document):
    meta = {'collection': 'Users'}
    name = StringField(required=True)
    username = StringField(required=True, unique=True)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    #  it overrides the usage of the original update function
    def update(self, **kwargs):
        kwargs["updated_at"] = datetime.datetime.now()  # forcefully update this `updated_at` Field
        return super(UserModel, self).update(**kwargs)
