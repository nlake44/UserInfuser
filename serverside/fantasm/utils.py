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
from fantasm import constants
from google.appengine.api.taskqueue.taskqueue import Queue

class NoOpQueue( Queue ):
    """ A Queue instance that does not Queue """
    
    def add(self, task, transactional=False):
        """ see taskqueue.Queue.add """
        pass
       
def knuthHash(number):
    """A decent hash function for integers."""
    return (number * 2654435761) % 2**32

def boolConverter(boolStr):
    """ A converter that maps some common bool string to True """
    return {'1': True, 'True': True, 'true': True}.get(boolStr, False)

def outputAction(action):
    """ Outputs the name of the action 
    
    @param action: an FSMAction instance 
    """
    if action:
        return str(action.__class__.__name__).split('.')[-1]

def outputTransitionConfig(transitionConfig):
    """ Outputs a GraphViz directed graph node
    
    @param transitionConfig: a config._TransitionConfig instance
    @return: a string
    """
    label = transitionConfig.event
    if transitionConfig.action:
        label += '/ ' + outputAction(transitionConfig.action)
    return '"%(fromState)s" -> "%(toState)s" [label="%(label)s"];' % \
            {'fromState': transitionConfig.fromState.name, 
             'toState': transitionConfig.toState.name, 
             'label': label}
            
def outputStateConfig(stateConfig, colorMap=None):
    """ Outputs a GraphViz directed graph node
    
    @param stateConfig: a config._StateConfig instance
    @return: a string
    """
    colorMap = colorMap or {}
    actions = []
    if stateConfig.entry:
        actions.append('entry/ %(entry)s' % {'entry': outputAction(stateConfig.entry)})
    if stateConfig.action:
        actions.append('do/ %(do)s' % {'do': outputAction(stateConfig.action)})
    if stateConfig.exit:
        actions.append('exit/ %(exit)s' % {'exit': outputAction(stateConfig.exit)})
    label = '%(stateName)s|%(actions)s' % {'stateName': stateConfig.name, 'actions': '\\l'.join(actions)}
    if stateConfig.continuation:
        label += '|continuation = True'
    if stateConfig.fanInPeriod != constants.NO_FAN_IN:
        label += '|fan in period = %(fanin)ds' % {'fanin': stateConfig.fanInPeriod}
    shape = 'Mrecord'
    if colorMap.get(stateConfig.name):
        return '"%(stateName)s" [style=filled,fillcolor="%(fillcolor)s",shape=%(shape)s,label="{%(label)s}"];' % \
               {'stateName': stateConfig.name,
                'fillcolor': colorMap.get(stateConfig.name, 'white'),
                'shape': shape,
                'label': label}
    else:
        return '"%(stateName)s" [shape=%(shape)s,label="{%(label)s}"];' % \
               {'stateName': stateConfig.name,
                'shape': shape,
                'label': label}

def outputMachineConfig(machineConfig, colorMap=None, skipStateNames=None):
    """ Outputs a GraphViz directed graph of the state machine 
    
    @param machineConfig: a config._MachineConfig instance
    @return: a string
    """
    skipStateNames = skipStateNames or ()
    lines = []
    lines.append('digraph G {')
    lines.append('label="%(machineName)s"' % {'machineName': machineConfig.name})
    lines.append('labelloc="t"')
    lines.append('"__start__" [label="start",shape=circle,style=filled,fillcolor=black,fontcolor=white,fontsize=9];')
    lines.append('"__end__" [label="end",shape=doublecircle,style=filled,fillcolor=black,fontcolor=white,fontsize=9];')
    for stateConfig in machineConfig.states.values():
        if stateConfig.name in skipStateNames:
            continue
        lines.append(outputStateConfig(stateConfig, colorMap=colorMap))
        if stateConfig.initial:
            lines.append('"__start__" -> "%(stateName)s"' % {'stateName': stateConfig.name})
        if stateConfig.final:
            lines.append('"%(stateName)s" -> "__end__"' % {'stateName': stateConfig.name})
    for transitionConfig in machineConfig.transitions.values():
        if transitionConfig.fromState.name in skipStateNames or \
           transitionConfig.toState.name in skipStateNames:
            continue
        lines.append(outputTransitionConfig(transitionConfig))
    lines.append('}')
    return '\n'.join(lines) 