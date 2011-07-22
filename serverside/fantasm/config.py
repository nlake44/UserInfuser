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

import os
import yaml
import logging
import simplejson
import datetime
from fantasm import exceptions, constants, utils

TASK_ATTRIBUTES = (
    (constants.TASK_RETRY_LIMIT_ATTRIBUTE, 'taskRetryLimit', constants.DEFAULT_TASK_RETRY_LIMIT, 
     exceptions.InvalidTaskRetryLimitError),
    (constants.MIN_BACKOFF_SECONDS_ATTRIBUTE, 'minBackoffSeconds', constants.DEFAULT_MIN_BACKOFF_SECONDS, 
     exceptions.InvalidMinBackoffSecondsError),
    (constants.MAX_BACKOFF_SECONDS_ATTRIBUTE, 'maxBackoffSeconds', constants.DEFAULT_MAX_BACKOFF_SECONDS, 
     exceptions.InvalidMaxBackoffSecondsError),
    (constants.TASK_AGE_LIMIT_ATTRIBUTE, 'taskAgeLimit', constants.DEFAULT_TASK_AGE_LIMIT, 
     exceptions.InvalidTaskAgeLimitError),
    (constants.MAX_DOUBLINGS_ATTRIBUTE, 'maxDoublings', constants.DEFAULT_MAX_DOUBLINGS, 
     exceptions.InvalidMaxDoublingsError),
)

_config = None

def currentConfiguration(filename=None):
    """ Retrieves the current configuration specified by the fsm.yaml file. """
    # W0603: 32:currentConfiguration: Using the global statement
    global _config # pylint: disable-msg=W0603
    
    # always reload the config for dev_appserver to grab recent dev changes
    if _config and not constants.DEV_APPSERVER:
        return _config
        
    _config = loadYaml(filename=filename)
    return _config

# following function is borrowed from mapreduce code
# ...
# N.B. Sadly, we currently don't have and ability to determine
# application root dir at run time. We need to walk up the directory structure
# to find it.
def _findYaml(yamlNames=constants.YAML_NAMES):
    """Traverse up from current directory and find fsm.yaml file.

    Returns:
      the path of fsm.yaml file or None if not found.
    """
    directory = os.path.dirname(__file__)
    while directory:
        for yamlName in yamlNames:
            yamlPath = os.path.join(directory, yamlName)
            if os.path.exists(yamlPath):
                return yamlPath
        parent = os.path.dirname(directory)
        if parent == directory:
            break
        directory = parent
    return None

def loadYaml(filename=None, importedAlready=None):
    """ Loads the YAML and constructs a configuration from it. """
    if not filename:
        filename = _findYaml()
    if not filename:
        raise exceptions.YamlFileNotFoundError('fsm.yaml')
      
    try:
        yamlFile = open(filename)
    except IOError:
        raise exceptions.YamlFileNotFoundError(filename)
    try:
        configDict = yaml.load(yamlFile.read())
    finally:
        yamlFile.close()
        
    return Configuration(configDict, importedAlready=importedAlready)
        
class Configuration(object):
    """ An overall configuration that corresponds to a fantasm.yaml file. """
    
    def __init__(self, configDict, importedAlready=None):
        """ Constructs the configuration from a dictionary of values. """
        
        importedAlready = importedAlready or []
        
        if constants.STATE_MACHINES_ATTRIBUTE not in configDict:
            raise exceptions.StateMachinesAttributeRequiredError()
        
        self.rootUrl = configDict.get(constants.ROOT_URL_ATTRIBUTE, constants.DEFAULT_ROOT_URL)
        if not self.rootUrl.endswith('/'):
            self.rootUrl += '/'
            
        self.machines = {}
        
        # import built-in machines
        self._importBuiltInMachines(importedAlready=importedAlready)
        
        for machineDict in configDict[constants.STATE_MACHINES_ATTRIBUTE]:
            
            # bring in all the imported machines
            if machineDict.get(constants.IMPORT_ATTRIBUTE):
                self._importYaml(machineDict[constants.IMPORT_ATTRIBUTE], importedAlready=importedAlready)
                continue
                
            machine = _MachineConfig(machineDict, rootUrl=self.rootUrl)
            if machine.name in self.machines:
                raise exceptions.MachineNameNotUniqueError(machine.name)
                
            # add the states
            for stateDict in machineDict.get(constants.MACHINE_STATES_ATTRIBUTE, []):
                machine.addState(stateDict)
                
            if not machine.initialState:
                raise exceptions.MachineHasNoInitialStateError(machine.name)
            
            if not machine.finalStates:
                raise exceptions.MachineHasNoFinalStateError(machine.name)
            
            # add the transitions (2-phase parsing :( )
            for stateDict in machineDict.get(constants.MACHINE_STATES_ATTRIBUTE, []):
                for transDict in stateDict.get(constants.STATE_TRANSITIONS_ATTRIBUTE, []):
                    machine.addTransition(transDict, stateDict[constants.STATE_NAME_ATTRIBUTE])
                
            self.machines[machine.name] = machine
            
    def __addMachinesFromImportedConfig(self, importedCofig):
        """ Adds new machines from an imported configuration. """
        for machineName, machine in importedCofig.machines.items():
            if machineName in self.machines:
                raise exceptions.MachineNameNotUniqueError(machineName)
            self.machines[machineName] = machine
            
    def _importYaml(self, importYamlFile, importedAlready=None):
        """ Imports a yaml file """
        yamlFile = _findYaml(yamlNames=[importYamlFile])
        if not yamlFile:
            raise exceptions.YamlFileNotFoundError(importYamlFile)
        if yamlFile in importedAlready:
            raise exceptions.YamlFileCircularImportError(importYamlFile)
        importedAlready.append(yamlFile)
        importedConfig = loadYaml(filename=yamlFile, importedAlready=importedAlready)
        self.__addMachinesFromImportedConfig(importedConfig)
            
    BUILTIN_MACHINES = (
        'scrubber.yaml',
    )
            
    def _importBuiltInMachines(self, importedAlready=None):
        """ Imports built-in machines. """
        directory = os.path.dirname(__file__)
        for key in self.BUILTIN_MACHINES:
            yamlFile = os.path.join(directory, key)
            if yamlFile in importedAlready:
                continue
            importedAlready.append(yamlFile)
            importedConfig = loadYaml(filename=yamlFile, importedAlready=importedAlready)
            self.__addMachinesFromImportedConfig(importedConfig)

def _resolveClass(className, namespace):
    """ Given a string representation of a class, locates and returns the class object. """
    
    # some shortcuts for context_types
    shortTypes = {
        'dict': simplejson.loads,
        'int': int,
        'float': float,
        'bool': utils.boolConverter, 
        'long': long,
        'json': simplejson.loads,
        'datetime': lambda x: datetime.datetime.utcfromtimestamp(int(x)),
    }
    if className in shortTypes:
        return shortTypes[className] # FIXME: is this valid with methods?
    
    if '.' in className:
        fullyQualifiedClass = className
    elif namespace:
        fullyQualifiedClass = '%s.%s' % (namespace, className)
    else:
        fullyQualifiedClass = className
    
    moduleName = fullyQualifiedClass[:fullyQualifiedClass.rfind('.')]
    className = fullyQualifiedClass[fullyQualifiedClass.rfind('.')+1:]
    
    try:
        module = __import__(moduleName, globals(), locals(), [className])
    except ImportError, e:
        raise exceptions.UnknownModuleError(moduleName, e)
        
    try:
        resolvedClass = getattr(module, className)
        return resolvedClass
    except AttributeError:
        raise exceptions.UnknownClassError(moduleName, className)
    
def _resolveObject(objectName, namespace, expectedType=basestring):
    """ Given a string name/path of a object, locates and returns the value of the object. 
    
    @param objectName: ie. MODULE_LEVEL_CONSTANT, ActionName.CLASS_LEVEL_CONSTANT
    @param namespace: ie. fully.qualified.python.module 
    """
    
    if '.' in objectName:
        classOrObjectName = objectName[:objectName.rfind('.')]
        objectName2 = objectName[objectName.rfind('.')+1:]
    else:
        classOrObjectName = objectName
        
    resolvedClassOrObject = _resolveClass(classOrObjectName, namespace)
    
    if isinstance(resolvedClassOrObject, expectedType):
        return resolvedClassOrObject
    
    try:
        resolvedObject = getattr(resolvedClassOrObject, objectName2)
    except AttributeError:
        raise exceptions.UnknownObjectError(objectName)
        
    if not isinstance(resolvedObject, expectedType):
        raise exceptions.UnexpectedObjectTypeError(objectName, expectedType)
        
    return resolvedObject
        
class _MachineConfig(object):
    """ Configuration of a machine. """
    
    def __init__(self, initDict, rootUrl=None):
        """ Configures the basic attributes of a machine. States and transitions are not handled
            here, but are added by an external client.
        """
        
        # machine name
        self.name = initDict.get(constants.MACHINE_NAME_ATTRIBUTE)
        if not self.name:
            raise exceptions.MachineNameRequiredError()
        if not constants.NAME_RE.match(self.name):
            raise exceptions.InvalidMachineNameError(self.name)
        
        # check for bad attributes
        badAttributes = set()
        for attribute in initDict.iterkeys():
            if attribute not in constants.VALID_MACHINE_ATTRIBUTES:
                badAttributes.add(attribute)
        if badAttributes:
            raise exceptions.InvalidMachineAttributeError(self.name, badAttributes)
            
        # machine queue, namespace
        self.queueName = initDict.get(constants.QUEUE_NAME_ATTRIBUTE, constants.DEFAULT_QUEUE_NAME)
        self.namespace = initDict.get(constants.NAMESPACE_ATTRIBUTE)
        
        # logging
        self.logging = initDict.get(constants.MACHINE_LOGGING_NAME_ATTRIBUTE, constants.LOGGING_DEFAULT)
        if self.logging not in constants.VALID_LOGGING_VALUES:
            raise exceptions.InvalidLoggingError(self.name, self.logging)
        
        # machine task_retry_limit, min_backoff_seconds, max_backoff_seconds, task_age_limit, max_doublings
        for (constant, attribute, default, exception) in TASK_ATTRIBUTES:
            setattr(self, attribute, default)
            if constant in initDict:
                setattr(self, attribute, initDict[constant])
                try:
                    i = int(getattr(self, attribute))
                    setattr(self, attribute, i)
                except ValueError:
                    raise exception(self.name, getattr(self, attribute))

        # if both max_retries and task_retry_limit specified, raise an exception
        if constants.MAX_RETRIES_ATTRIBUTE in initDict and constants.TASK_RETRY_LIMIT_ATTRIBUTE in initDict:
            raise exceptions.MaxRetriesAndTaskRetryLimitMutuallyExclusiveError(self.name)
        
        # machine max_retries - sets taskRetryLimit internally
        if constants.MAX_RETRIES_ATTRIBUTE in initDict:
            logging.warning('max_retries is deprecated. Use task_retry_limit instead.')
            self.taskRetryLimit = initDict[constants.MAX_RETRIES_ATTRIBUTE]
            try:
                self.taskRetryLimit = int(self.taskRetryLimit)
            except ValueError:
                raise exceptions.InvalidMaxRetriesError(self.name, self.taskRetryLimit)
                        
        self.states = {}
        self.transitions = {}
        self.initialState = None
        self.finalStates = []
        
        # context types
        self.contextTypes = initDict.get(constants.MACHINE_CONTEXT_TYPES_ATTRIBUTE, {})
        for contextName, contextType in self.contextTypes.iteritems():
            self.contextTypes[contextName] = _resolveClass(contextType, self.namespace)
        
        self.rootUrl = rootUrl
        if not self.rootUrl:
            self.rootUrl = constants.DEFAULT_ROOT_URL
        elif not rootUrl.endswith('/'):
            self.rootUrl += '/'
            
    @property
    def maxRetries(self):
        """ maxRetries is a synonym for taskRetryLimit """
        return self.taskRetryLimit
        
    def addState(self, stateDict):
        """ Adds a state to this machine (using a dictionary representation). """
        state = _StateConfig(stateDict, self)
        if state.name in self.states:
            raise exceptions.StateNameNotUniqueError(self.name, state.name)
        self.states[state.name] = state
        
        if state.initial:
            if self.initialState:
                raise exceptions.MachineHasMultipleInitialStatesError(self.name)
            self.initialState = state
        if state.final:
            self.finalStates.append(state)
        
        return state
        
    def addTransition(self, transDict, fromStateName):
        """ Adds a transition to this machine (using a dictionary representation). """
        transition = _TransitionConfig(transDict, self, fromStateName)
        if transition.name in self.transitions:
            raise exceptions.TransitionNameNotUniqueError(self.name, transition.name)
        self.transitions[transition.name] = transition
        
        return transition
        
    @property
    def url(self):
        """ Returns the url for this machine. """
        return '%sfsm/%s/' % (self.rootUrl, self.name)
        
class _StateConfig(object):
    """ Configuration of a state. """
    
    # R0912:268:_StateConfig.__init__: Too many branches (22/20)
    def __init__(self, stateDict, machine): # pylint: disable-msg=R0912
        """ Builds a _StateConfig from a dictionary representation. This state is not added to the machine. """
        
        self.machineName = machine.name
        
        # state name
        self.name = stateDict.get(constants.STATE_NAME_ATTRIBUTE)
        if not self.name:
            raise exceptions.StateNameRequiredError(self.machineName)
        if not constants.NAME_RE.match(self.name):
            raise exceptions.InvalidStateNameError(self.machineName, self.name)
            
        # check for bad attributes
        badAttributes = set()
        for attribute in stateDict.iterkeys():
            if attribute not in constants.VALID_STATE_ATTRIBUTES:
                badAttributes.add(attribute)
        if badAttributes:
            raise exceptions.InvalidStateAttributeError(self.machineName, self.name, badAttributes)
        
        self.final = bool(stateDict.get(constants.STATE_FINAL_ATTRIBUTE, False))

        # state action
        actionName = stateDict.get(constants.STATE_ACTION_ATTRIBUTE)
        if not actionName and not self.final:
            raise exceptions.StateActionRequired(self.machineName, self.name)
            
        # state namespace, initial state flag, final state flag, continuation flag
        self.namespace = stateDict.get(constants.NAMESPACE_ATTRIBUTE, machine.namespace)
        self.initial = bool(stateDict.get(constants.STATE_INITIAL_ATTRIBUTE, False))
        self.continuation = bool(stateDict.get(constants.STATE_CONTINUATION_ATTRIBUTE, False))
        
        # state fan_in
        self.fanInPeriod = stateDict.get(constants.STATE_FAN_IN_ATTRIBUTE, constants.NO_FAN_IN)
        try:
            self.fanInPeriod = int(self.fanInPeriod)
        except ValueError:
            raise exceptions.InvalidFanInError(self.machineName, self.name, self.fanInPeriod)
            
        # check that a state is not BOTH fan_in and continuation
        if self.continuation and self.fanInPeriod != constants.NO_FAN_IN:
            raise exceptions.FanInContinuationNotSupportedError(self.machineName, self.name)
        
        # state action
        if stateDict.get(constants.STATE_ACTION_ATTRIBUTE):
            self.action = _resolveClass(actionName, self.namespace)()
            if not hasattr(self.action, 'execute'):
                raise exceptions.InvalidActionInterfaceError(self.machineName, self.name)
        else:
            self.action = None
        
        if self.continuation:
            if not hasattr(self.action, 'continuation'):
                raise exceptions.InvalidContinuationInterfaceError(self.machineName, self.name)
        else:
            if hasattr(self.action, 'continuation'):
                logging.warning('State\'s action class has a continuation attribute, but the state is ' + 
                                'not marked as continuation=True. This continuation method will not be ' +
                                'executed. (Machine %s, State %s)', self.machineName, self.name)
            
        # state entry
        if stateDict.get(constants.STATE_ENTRY_ATTRIBUTE):
            self.entry = _resolveClass(stateDict[constants.STATE_ENTRY_ATTRIBUTE], self.namespace)()
            if not hasattr(self.entry, 'execute'):
                raise exceptions.InvalidEntryInterfaceError(self.machineName, self.name)
        else:
            self.entry = None
        
        # state exit
        if stateDict.get(constants.STATE_EXIT_ATTRIBUTE):
            self.exit = _resolveClass(stateDict[constants.STATE_EXIT_ATTRIBUTE], self.namespace)()
            if not hasattr(self.exit, 'execute'):
                raise exceptions.InvalidExitInterfaceError(self.machineName, self.name)
            if self.continuation:
                raise exceptions.UnsupportedConfigurationError(self.machineName, self.name,
                    'Exit actions on continuation states are not supported.'
                )
            if self.fanInPeriod != constants.NO_FAN_IN:
                raise exceptions.UnsupportedConfigurationError(self.machineName, self.name,
                    'Exit actions on fan_in states are not supported.'
                )
        else:
            self.exit = None

class _TransitionConfig(object):
    """ Configuration of a transition. """
    
    # R0912:326:_TransitionConfig.__init__: Too many branches (22/20)
    def __init__(self, transDict, machine, fromStateName): # pylint: disable-msg=R0912
        """ Builds a _TransitionConfig from a dictionary representation. 
            This transition is not added to the machine. """

        self.machineName = machine.name
        
        # check for bad attributes
        badAttributes = set()
        for attribute in transDict.iterkeys():
            if attribute not in constants.VALID_TRANS_ATTRIBUTES:
                badAttributes.add(attribute)
        if badAttributes:
            raise exceptions.InvalidTransitionAttributeError(self.machineName, fromStateName, badAttributes)

        # transition event
        event = transDict.get(constants.TRANS_EVENT_ATTRIBUTE)
        if not event:
            raise exceptions.TransitionEventRequiredError(machine.name, fromStateName)
        try:
            # attempt to import the value of the event
            self.event = _resolveObject(event, machine.namespace)
        except (exceptions.UnknownModuleError, exceptions.UnknownClassError, exceptions.UnknownObjectError):
            # otherwise just use the value from the yaml
            self.event = event
        if not constants.NAME_RE.match(self.event):
            raise exceptions.InvalidTransitionEventNameError(self.machineName, fromStateName, self.event)
            
        # transition name
        self.name = '%s--%s' % (fromStateName, self.event)
        if not self.name:
            raise exceptions.TransitionNameRequiredError(self.machineName)
        if not constants.NAME_RE.match(self.name):
            raise exceptions.InvalidTransitionNameError(self.machineName, self.name)

        # transition from state
        if not fromStateName:
            raise exceptions.TransitionFromRequiredError(self.machineName, self.name)
        if fromStateName not in machine.states:
            raise exceptions.TransitionUnknownFromStateError(self.machineName, self.name, fromStateName)
        self.fromState = machine.states[fromStateName]
        
        # transition to state
        toStateName = transDict.get(constants.TRANS_TO_ATTRIBUTE)
        if not toStateName:
            raise exceptions.TransitionToRequiredError(self.machineName, self.name)
        if toStateName not in machine.states:
            raise exceptions.TransitionUnknownToStateError(self.machineName, self.name, toStateName)
        self.toState = machine.states[toStateName]
        
        # transition namespace
        self.namespace = transDict.get(constants.NAMESPACE_ATTRIBUTE, machine.namespace)

        # transition task_retry_limit, min_backoff_seconds, max_backoff_seconds, task_age_limit, max_doublings
        # W0612:439:_TransitionConfig.__init__: Unused variable 'default'
        for (constant, attribute, default, exception) in TASK_ATTRIBUTES: # pylint: disable-msg=W0612
            setattr(self, attribute, getattr(machine, attribute)) # default from the machine
            if constant in transDict:
                setattr(self, attribute, transDict[constant])
                try:
                    i = int(getattr(self, attribute))
                    setattr(self, attribute, i)
                except ValueError:
                    raise exception(self.machineName, getattr(self, attribute))

        # if both max_retries and task_retry_limit specified, raise an exception
        if constants.MAX_RETRIES_ATTRIBUTE in transDict and constants.TASK_RETRY_LIMIT_ATTRIBUTE in transDict:
            raise exceptions.MaxRetriesAndTaskRetryLimitMutuallyExclusiveError(self.machineName)
            
        # transition maxRetries
        if constants.MAX_RETRIES_ATTRIBUTE in transDict:
            logging.warning('max_retries is deprecated. Use task_retry_limit instead.')
            self.taskRetryLimit = transDict[constants.MAX_RETRIES_ATTRIBUTE]
            try:
                self.taskRetryLimit = int(self.taskRetryLimit)
            except ValueError:
                raise exceptions.InvalidMaxRetriesError(self.name, self.taskRetryLimit)
            
        # transition countdown
        self.countdown = transDict.get(constants.TRANS_COUNTDOWN_ATTRIBUTE, constants.DEFAULT_COUNTDOWN)
        try:
            self.countdown = int(self.countdown)
        except ValueError:
            raise exceptions.InvalidCountdownError(self.countdown, self.machineName, self.fromState.name)
        if self.countdown and self.toState.fanInPeriod != constants.NO_FAN_IN:
            raise exceptions.UnsupportedConfigurationError(self.machineName, self.fromState.name,
                'Countdown cannot be specified on a transition to a fan_in state.'
            )
            
        # transition specific queue
        self.queueName = transDict.get(constants.QUEUE_NAME_ATTRIBUTE, machine.queueName)

        # resolve the class for action, if specified
        if constants.TRANS_ACTION_ATTRIBUTE in transDict:
            self.action = _resolveClass(transDict[constants.TRANS_ACTION_ATTRIBUTE], self.namespace)()
            if self.fromState.continuation:
                raise exceptions.UnsupportedConfigurationError(self.machineName, self.fromState.name,
                    'Transition actions on transitions from continuation states are not supported.'
                )
            if self.toState.continuation:
                raise exceptions.UnsupportedConfigurationError(self.machineName, self.fromState.name,
                    'Transition actions on transitions to continuation states are not supported.'
                )
            if self.fromState.fanInPeriod != constants.NO_FAN_IN:
                raise exceptions.UnsupportedConfigurationError(self.machineName, self.fromState.name,
                    'Transition actions on transitions from fan_in states are not supported.'
                )
            if self.toState.fanInPeriod != constants.NO_FAN_IN:
                raise exceptions.UnsupportedConfigurationError(self.machineName, self.fromState.name,
                    'Transition actions on transitions to fan_in states are not supported.'
                )
        else:
            self.action = None
            
        # test for exit actions when transitions to a continuation or a fan_in
        if self.toState.continuation and self.fromState.exit:
            raise exceptions.UnsupportedConfigurationError(self.machineName, self.fromState.name,
                'Exit actions on states with a transition to a continuation state are not supported.'
            )
        if self.toState.fanInPeriod != constants.NO_FAN_IN and self.fromState.exit:
            raise exceptions.UnsupportedConfigurationError(self.machineName, self.fromState.name,
                'Exit actions on states with a transition to a fan_in state are not supported.'
            )

    @property
    def maxRetries(self):
        """ maxRetries is a synonym for taskRetryLimit """
        return self.taskRetryLimit
