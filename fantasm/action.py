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

class FSMAction(object):
    """ Defines the interface for all user actions. """
    
    def execute(self, context, obj):
        """ Executes some action. The return value is ignored, _except_ for the main state action.
        
        @param context The FSMContext (i.e., machine). context.get() and context.put() can be used to get data
                       from/to the context.
        @param obj: An object which the action can operate on
        
        For the main state action, the return value should be a string representing the event to be dispatched.
        Actions performed should be careful to be idempotent: because of potential retry mechanisms 
        (notably with TaskQueueFSMContext), individual execute methods may get executed more than once with 
        exactly the same context.
        """
        raise NotImplementedError()
    
class ContinuationFSMAction(FSMAction):
    """ Defines the interface for all continuation actions. """
    
    def continuation(self, context, obj, token=None):
        """ Accepts a token (may be None) and returns the next token for the continutation. 
        
        @param token: the continuation token
        @param context The FSMContext (i.e., machine). context.get() and context.put() can be used to get data
                       from/to the context.
        @param obj: An object which the action can operate on
        """
        raise NotImplementedError()
    
class DatastoreContinuationFSMAction(ContinuationFSMAction):
    """ A datastore continuation. """
    
    def continuation(self, context, obj, token=None):
        """ Accepts a token (an optional cursor) and returns the next token for the continutation. 
        The results of the query are stored on obj.results.
        """
        # the continuation query comes
        query = self.getQuery(context, obj)
        cursor = token
        if cursor:
            query.with_cursor(cursor)
        limit = self.getBatchSize(context, obj)
        
        # place results on obj.results
        obj['results'] = query.fetch(limit)
        obj.results = obj['results'] # deprecated interface
        
        # add first obj.results item on obj.result - convenient for batch size 1
        if obj['results'] and len(obj['results']) > 0:
            obj['result'] = obj['results'][0]
        else:
            obj['result'] = None
        obj.result = obj['result'] # deprecated interface
            
        if len(obj['results']) == limit:
            return query.cursor()
        
    def getQuery(self, context, obj):
        """ Returns a GqlQuery """
        raise NotImplementedError()
    
    # W0613: 78:DatastoreContinuationFSMAction.getBatchSize: Unused argument 'obj'
    def getBatchSize(self, context, obj): # pylint: disable-msg=W0613
        """ Returns a batch size, default 1. Override for different values. """
        return 1
