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

import time
import logging
import simplejson
from google.appengine.ext import deferred, webapp, db
from google.appengine.api.capabilities import CapabilitySet
from fantasm import config, constants
from fantasm.fsm import FSM
from fantasm.utils import NoOpQueue
from fantasm.constants import NON_CONTEXT_PARAMS, STATE_PARAM, EVENT_PARAM, INSTANCE_NAME_PARAM, TASK_NAME_PARAM, \
                              RETRY_COUNT_PARAM, STARTED_AT_PARAM, IMMEDIATE_MODE_PARAM, MESSAGES_PARAM, \
                              HTTP_REQUEST_HEADER_PREFIX
from fantasm.exceptions import UnknownMachineError, RequiredServicesUnavailableRuntimeError, FSMRuntimeError
from fantasm.models import _FantasmTaskSemaphore, Encoder, _FantasmFanIn
from fantasm.lock import RunOnceSemaphore

REQUIRED_SERVICES = ('memcache', 'datastore_v3', 'taskqueue')

class TemporaryStateObject(dict):
    """ A simple object that is passed throughout a machine dispatch that can hold temporary
        in-flight data.
    """
    pass
    
def getMachineNameFromRequest(request):
    """ Returns the machine name embedded in the request.
    
    @param request: an HttpRequest
    @return: the machineName (as a string)
    """    
    path = request.path
    
    # strip off the mount-point
    currentConfig = config.currentConfiguration()
    mountPoint = currentConfig.rootUrl # e.g., '/fantasm/'
    if not path.startswith(mountPoint):
        raise FSMRuntimeError("rootUrl '%s' must match app.yaml mapping." % mountPoint)
    path = path[len(mountPoint):]
    
    # split on '/', the second item will be the machine name
    parts = path.split('/')
    return parts[1] # 0-based index

def getMachineConfig(request):
    """ Returns the machine configuration specified by a URI in a HttpReuest
    
    @param request: an HttpRequest
    @return: a config._machineConfig instance
    """ 
    
    # parse out the machine-name from the path {mount-point}/fsm/{machine-name}/startState/event/endState/
    # NOTE: /startState/event/endState/ is optional
    machineName = getMachineNameFromRequest(request)
    
    # load the configuration, lookup the machine-specific configuration
    # FIXME: sort out a module level cache for the configuration - it must be sensitive to YAML file changes
    # for developer-time experience
    currentConfig = config.currentConfiguration()
    try:
        machineConfig = currentConfig.machines[machineName]
        return machineConfig
    except KeyError:
        raise UnknownMachineError(machineName)

class FSMLogHandler(webapp.RequestHandler):
    """ The handler used for logging """
    def post(self):
        """ Runs the serialized function """
        deferred.run(self.request.body)
        
class FSMFanInCleanupHandler(webapp.RequestHandler):
    """ The handler used for logging """
    def post(self):
        """ Runs the serialized function """
        q = _FantasmFanIn.all().filter('workIndex =', self.request.POST[constants.WORK_INDEX_PARAM])
        db.delete(q)

class FSMGraphvizHandler(webapp.RequestHandler):
    """ The hander to output graphviz diagram of the finite state machine. """
    def get(self):
        """ Handles the GET request. """
        from fantasm.utils import outputMachineConfig
        machineConfig = getMachineConfig(self.request)
        content = outputMachineConfig(machineConfig, skipStateNames=[self.request.GET.get('skipStateName')])
        if self.request.GET.get('type', 'png') == 'png':
            self.response.out.write(
"""
<html>
<head></head>
<body onload="javascript:document.forms.chartform.submit();">
<form id='chartform' action='http://chart.apis.google.com/chart' method='POST'>
  <input type="hidden" name="cht" value="gv:dot"  />
  <input type="hidden" name="chl" value='%(chl)s'  />
  <input type="submit" value="Generate GraphViz .png" />
</form>
</body>
""" % {'chl': content.replace('\n', ' ')})
        else:
            self.response.out.write(content)
            
_fsm = None

def getCurrentFSM():
    """ Returns the current FSM singleton. """
    # W0603: 32:currentConfiguration: Using the global statement
    global _fsm # pylint: disable-msg=W0603
    
    # always reload the FSM for dev_appserver to grab recent dev changes
    if _fsm and not constants.DEV_APPSERVER:
        return _fsm
        
    currentConfig = config.currentConfiguration()
    _fsm = FSM(currentConfig=currentConfig)
    return _fsm
    
class FSMHandler(webapp.RequestHandler):
    """ The main worker handler, used to process queued machine events. """

    def get(self):
        """ Handles the GET request. """
        self.get_or_post(method='GET')
        
    def post(self):
        """ Handles the POST request. """
        self.get_or_post(method='POST')
        
    def initialize(self, request, response):
        """Initializes this request handler with the given Request and Response."""
        super(FSMHandler, self).initialize(request, response)
        # pylint: disable-msg=W0201
        # - this is the preferred location to initialize the handler in the webapp framework
        self.fsm = None
        
    def handle_exception(self, exception, debug_mode): # pylint: disable-msg=C0103
        """ Delegates logging to the FSMContext logger """
        self.error(500)
        logger = logging
        if self.fsm:
            logger = self.fsm.logger
        logger.exception("FSMHandler caught Exception")
        if debug_mode:
            import traceback, sys, cgi
            lines = ''.join(traceback.format_exception(*sys.exc_info()))
            self.response.clear()
            self.response.out.write('<pre>%s</pre>' % (cgi.escape(lines, quote=True)))
        
    def get_or_post(self, method='POST'):
        """ Handles the GET/POST request. 
        
        FIXME: this is getting a touch long
        """
        
        # ensure that we have our services for the next 30s (length of a single request)
        unavailable = set()
        for service in REQUIRED_SERVICES:
            if not CapabilitySet(service).is_enabled():
                unavailable.add(service)
        if unavailable:
            raise RequiredServicesUnavailableRuntimeError(unavailable)
        
        # the case of headers is inconsistent on dev_appserver and appengine
        # ie 'X-AppEngine-TaskRetryCount' vs. 'X-AppEngine-Taskretrycount'
        lowerCaseHeaders = dict([(key.lower(), value) for key, value in self.request.headers.items()])

        taskName = lowerCaseHeaders.get('x-appengine-taskname')
        retryCount = int(lowerCaseHeaders.get('x-appengine-taskretrycount', 0))
        
        # Taskqueue can invoke multiple tasks of the same name occassionally. Here, we'll use
        # a datastore transaction as a semaphore to determine if we should actually execute this or not.
        if taskName:
            semaphoreKey = '%s--%s' % (taskName, retryCount)
            semaphore = RunOnceSemaphore(semaphoreKey, None)
            if not semaphore.writeRunOnceSemaphore(payload='fantasm')[0]:
                # we can simply return here, this is a duplicate fired task
                logging.info('A duplicate task "%s" has been queued by taskqueue infrastructure. Ignoring.', taskName)
                self.response.status_code = 200
                return
            
        # pull out X-Fantasm-* headers
        headers = None
        for key, value in self.request.headers.items():
            if key.startswith(HTTP_REQUEST_HEADER_PREFIX):
                headers = headers or {}
                if ',' in value:
                    headers[key] = [v.strip() for v in value.split(',')]
                else:
                    headers[key] = value.strip()
            
        requestData = {'POST': self.request.POST, 'GET': self.request.GET}[method]
        method = requestData.get('method') or method
        
        machineName = getMachineNameFromRequest(self.request)
        
        # get the incoming instance name, if any
        instanceName = requestData.get(INSTANCE_NAME_PARAM)
        
        # get the incoming state, if any
        fsmState = requestData.get(STATE_PARAM)
        
        # get the incoming event, if any
        fsmEvent = requestData.get(EVENT_PARAM)
        
        assert (fsmState and instanceName) or True # if we have a state, we should have an instanceName
        assert (fsmState and fsmEvent) or True # if we have a state, we should have an event
        
        obj = TemporaryStateObject()
        
        # make a copy, add the data
        fsm = getCurrentFSM().createFSMInstance(machineName, 
                                                currentStateName=fsmState, 
                                                instanceName=instanceName,
                                                method=method,
                                                obj=obj,
                                                headers=headers)
        
        # in "immediate mode" we try to execute as much as possible in the current request
        # for the time being, this does not include things like fork/spawn/contuniuations/fan-in
        immediateMode = IMMEDIATE_MODE_PARAM in requestData.keys()
        if immediateMode:
            obj[IMMEDIATE_MODE_PARAM] = immediateMode
            obj[MESSAGES_PARAM] = []
            fsm.Queue = NoOpQueue # don't queue anything else
        
        # pylint: disable-msg=W0201
        # - initialized outside of ctor is ok in this case
        self.fsm = fsm # used for logging in handle_exception
        
        # pull all the data off the url and stuff into the context
        for key, value in requestData.items():
            if key in NON_CONTEXT_PARAMS:
                continue # these are special, don't put them in the data
            
            # deal with ...a=1&a=2&a=3...
            value = requestData.get(key)
            valueList = requestData.getall(key)
            if len(valueList) > 1:
                value = valueList
                
            if key.endswith('[]'):
                key = key[:-2]
                value = [value]
                
            if key in fsm.contextTypes.keys():
                fsm.putTypedValue(key, value)
            else:
                fsm[key] = value
        
        if not (fsmState or fsmEvent):
            
            # just queue up a task to run the initial state transition using retries
            fsm[STARTED_AT_PARAM] = time.time()
            
            # initialize the fsm, which returns the 'pseudo-init' event
            fsmEvent = fsm.initialize()
            
        else:
            
            # add the retry counter into the machine context from the header
            obj[RETRY_COUNT_PARAM] = retryCount
            
            # add the actual task name to the context
            obj[TASK_NAME_PARAM] = taskName
            
            # dispatch and return the next event
            fsmEvent = fsm.dispatch(fsmEvent, obj)
            
        # loop and execute until there are no more events - any exceptions
        # will make it out to the user in the response - useful for debugging
        if immediateMode:
            while fsmEvent:
                fsmEvent = fsm.dispatch(fsmEvent, obj)
            self.response.headers['Content-Type'] = 'application/json'
            data = {
                'obj' : obj,
                'context': fsm,
            }
            self.response.out.write(simplejson.dumps(data, cls=Encoder))
