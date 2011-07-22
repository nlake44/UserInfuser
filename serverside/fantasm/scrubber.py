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

import datetime
from google.appengine.ext import db
from fantasm.action import DatastoreContinuationFSMAction
# W0611: 23: Unused import _FantasmLog
# we're importing these here so that db has a chance to see them before we query them
from fantasm.models import _FantasmInstance, _FantasmLog, _FantasmTaskSemaphore # pylint: disable-msg=W0611

# W0613: Unused argument 'obj'
# implementing interfaces
# pylint: disable-msg=W0613

class InitalizeScrubber(object):
    """ Use current time to set up task names. """
    def execute(self, context, obj):
        """ Computes the before date and adds to context. """
        age = context.pop('age', 90)
        context['before'] = datetime.datetime.utcnow() - datetime.timedelta(days=age)
        return 'next'
        
class EnumerateFantasmModels(object):
    """ Kick off a continuation for each model. """
    
    FANTASM_MODELS = (
        ('_FantasmInstance', 'createdTime'), 
        ('_FantasmLog', 'time'), 
        ('_FantasmTaskSemaphore', 'createdTime'),
        ('_FantasmFanIn', 'createdTime')
    )
    
    def continuation(self, context, obj, token=None):
        """ Continue over each model. """
        if not token:
            obj['model'] = self.FANTASM_MODELS[0][0]
            obj['dateattr'] = self.FANTASM_MODELS[0][1]
            return self.FANTASM_MODELS[1][0] if len(self.FANTASM_MODELS) > 1 else None
        else:
            # find next in list
            for i in range(0, len(self.FANTASM_MODELS)):
                if self.FANTASM_MODELS[i][0] == token:
                    obj['model'] = self.FANTASM_MODELS[i][0]
                    obj['dateattr'] = self.FANTASM_MODELS[i][1]
                    return self.FANTASM_MODELS[i+1][0] if i < len(self.FANTASM_MODELS)-1 else None
        return None # this occurs if a token passed in is not found in list - shouldn't happen
        
    def execute(self, context, obj):
        """ Pass control to next state. """
        if not 'model' in obj or not 'dateattr' in obj:
            return None
        context['model'] = obj['model']
        context['dateattr'] = obj['dateattr']
        return 'next'
        
class DeleteOldEntities(DatastoreContinuationFSMAction):
    """ Deletes entities of a given model older than a given date. """
    
    def getQuery(self, context, obj):
        """ Query for all entities before a given datetime. """
        model = context['model']
        dateattr = context['dateattr']
        before = context['before']
        query = 'SELECT __key__ FROM %s WHERE %s < :1' % (model, dateattr)
        return db.GqlQuery(query, before)
        
    def getBatchSize(self, context, obj):
        """ Batch size. """
        return 100
        
    def execute(self, context, obj):
        """ Delete the rows. """
        if obj['results']:
            db.delete(obj['results'])
