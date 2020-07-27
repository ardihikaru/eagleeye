"""
   This file helps the system to customize JSONEncoder format;
    - Formatted Primary Key Field (`_id`) from data type `ObjectID` into `String
    = Formatted any DateTimeField into isoformat
"""

from json import JSONEncoder
from bson import ObjectId
import datetime


class MongoEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, (datetime.date, datetime.datetime)):
            return o.isoformat()
