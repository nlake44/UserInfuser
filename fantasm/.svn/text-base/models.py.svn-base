""" Fantasm: A taskqueue-based Finite State Machine for App Engine Python

Docs and examples: http://code.google.com/p/fantasm/

Copyright 2010 VendAsta Technologies Inc.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

from google.appengine.ext import db
from google.appengine.api import datastore_types
import simplejson
import datetime

def decode(dct):
    """ Special handler for db.Key/datetime.datetime decoding """
    if '__set__' in dct:
        return set(dct['key'])
    if '__db.Key__' in dct:
        return db.Key(dct['key'])
    if '__db.Model__' in dct:
        return db.Key(dct['key']) # turns into a db.Key across serialization
    if '__datetime.datetime__' in dct:
        return datetime.datetime(**dct['datetime'])
    return dct

# W0232: 30:Encoder: Class has no __init__ method
class Encoder(simplejson.JSONEncoder): # pylint: disable-msg=W0232
    """ A JSONEncoder that handles db.Key """
    # E0202: 36:Encoder.default: An attribute inherited from JSONEncoder hide this method
    def default(self, obj): # pylint: disable-msg=E0202
        """ see simplejson.JSONEncoder.default """
        if isinstance(obj, set):
            return {'__set__': True, 'key': list(obj)}
        if isinstance(obj, db.Key):
            return {'__db.Key__': True, 'key': str(obj)}
        if isinstance(obj, db.Model):
            return {'__db.Model__': True, 'key': str(obj.key())} # turns into a db.Key across serialization
        if isinstance(obj, datetime.datetime) and \
           obj.tzinfo is None: # only UTC datetime objects are supported
            return {'__datetime.datetime__': True, 'datetime': {'year': obj.year,
                                                                'month': obj.month,
                                                                'day': obj.day,
                                                                'hour': obj.hour,
                                                                'minute': obj.minute,
                                                                'second': obj.second,
                                                                'microsecond': obj.microsecond}}
        return simplejson.JSONEncoder.default(self, obj)

class JSONProperty(db.Property):
    """
    From Google appengine cookbook... a Property for storing dicts in the datastore
    """
    data_type = datastore_types.Text
    
    def get_value_for_datastore(self, modelInstance):
        """ see Property.get_value_for_datastore """
        value = super(JSONProperty, self).get_value_for_datastore(modelInstance)
        return db.Text(self._deflate(value))
    
    def validate(self, value):
        """ see Property.validate """
        return self._inflate(value)
    
    def make_value_from_datastore(self, value):
        """ see Property.make_value_from_datastore """
        return self._inflate(value)
    
    def _inflate(self, value):
        """ decodes string -> dict """
        if value is None:
            return {}
        if isinstance(value, unicode) or isinstance(value, str):
            return simplejson.loads(value, object_hook=decode)
        return value
    
    def _deflate(self, value):
        """ encodes dict -> string """
        return simplejson.dumps(value, cls=Encoder)
    
    
class _FantasmFanIn( db.Model ):
    """ A model used to store FSMContexts for fan in """
    workIndex = db.StringProperty()
    context = JSONProperty(indexed=False)
    # FIXME: createdTime only needed for scrubbing, but indexing might be a performance hit
    #        http://ikaisays.com/2011/01/25/app-engine-datastore-tip-monotonically-increasing-values-are-bad/
    createdTime = db.DateTimeProperty(auto_now_add=True)
    
class _FantasmInstance( db.Model ):
    """ A model used to to store FSMContext instances """
    instanceName = db.StringProperty()
    # FIXME: createdTime only needed for scrubbing, but indexing might be a performance hit
    #        http://ikaisays.com/2011/01/25/app-engine-datastore-tip-monotonically-increasing-values-are-bad/
    createdTime = db.DateTimeProperty(auto_now_add=True)
    
class _FantasmLog( db.Model ):
    """ A model used to store log messages """
    taskName = db.StringProperty()
    instanceName = db.StringProperty()
    machineName = db.StringProperty()
    stateName = db.StringProperty()
    actionName = db.StringProperty()
    transitionName = db.StringProperty()
    time = db.DateTimeProperty()
    level = db.IntegerProperty()
    message = db.TextProperty()
    stack = db.TextProperty()
    tags = db.StringListProperty()

class _FantasmTaskSemaphore( db.Model ):
    """ A model that simply stores the task name so that we can guarantee only-once semantics. """
    # FIXME: createdTime only needed for scrubbing, but indexing might be a performance hit
    #        http://ikaisays.com/2011/01/25/app-engine-datastore-tip-monotonically-increasing-values-are-bad/
    createdTime = db.DateTimeProperty(auto_now_add=True)
    payload = db.StringProperty(indexed=False)
