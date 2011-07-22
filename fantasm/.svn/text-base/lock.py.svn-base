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
import random
import time
import logging

from google.appengine.api import memcache
from google.appengine.ext import db

from fantasm.models import _FantasmTaskSemaphore
from fantasm import constants
from fantasm.exceptions import FanInWriteLockFailureRuntimeError
from fantasm.exceptions import FanInReadLockFailureRuntimeError

# a variety of locking mechanisms to enforce idempotency (of the framework) in the face of retries

class ReadWriteLock( object ):
    """ A read/write lock that allows
    
    1. non-blocking write (for speed of fan-out)
    2. blocking read (speed not reqd in fan-in)
    """
    
    INDEX_PARAM = 'index'
    LOCK_PARAM = 'lock'
    
    # 20 iterations * 0.25s = 5s total wait time
    BUSY_WAIT_ITERS = 20
    BUSY_WAIT_ITER_SECS = 0.250
    
    def __init__(self, taskNameBase, context, obj=None):
        """ ctor 
        
        @param taskNameBase: the key for fan-in, based on the task name of the fan-out items
        @param logger: a logging module or object
        """
        self.taskNameBase = taskNameBase
        self.context = context
        self.obj = obj
        
    def indexKey(self):
        """ Returns the lock index key """
        return ReadWriteLock.INDEX_PARAM + '-' + self.taskNameBase
    
    def lockKey(self, index):
        """ Returns the lock key """
        return self.taskNameBase + '-' + ReadWriteLock.LOCK_PARAM + '-' + str(index)
        
    def currentIndex(self):
        """ Returns the current lock index from memcache, or sets it if it is missing
        
        @return: an int, the current index
        """
        indexKey = self.indexKey()
        index = memcache.get(indexKey)
        if index is None:
            # using 'random.randint' here instead of '1' helps when the index is ejected from memcache
            # instead of restarting at the same counter, we jump (likely) far way from existing task job
            # names. 
            memcache.add(indexKey, random.randint(1, 2**32))
            index = memcache.get(indexKey)
        return index
    
    def acquireWriteLock(self, index, nextEvent=None, raiseOnFail=True):
        """ Acquires the write lock 
        
        @param index: an int, the current index
        @raise FanInWriteLockFailureRuntimeError: 
        """
        acquired = True
        lockKey = self.lockKey(index)
        writers = memcache.incr(lockKey, initial_value=2**16)
        if writers < 2**16:
            self.context.logger.error("Gave up waiting for write lock '%s'.", lockKey)
            acquired = False
            if raiseOnFail:
                # this will escape as a 500 error and the Task will be re-tried by appengine
                raise FanInWriteLockFailureRuntimeError(nextEvent, 
                                                        self.context.machineName, 
                                                        self.context.currentState.name, 
                                                        self.context.instanceName)
        return acquired
            
    def releaseWriteLock(self, index):
        """ Acquires the write lock 
        
        @param index: an int, the current index
        """
        released = True
        
        lockKey = self.lockKey(index)
        memcache.decr(lockKey)
        
        return released
    
    def acquireReadLock(self, index, nextEvent=None, raiseOnFail=False):
        """ Acquires the read lock
        
        @param index: an int, the current index
        """
        acquired = True
        
        lockKey = self.lockKey(index)
        indexKey = self.indexKey()
        
        # tell writers to use another index
        memcache.incr(indexKey)
        
        # tell writers they missed the boat
        memcache.decr(lockKey, 2**15) 
        
        # busy wait for writers
        for i in xrange(ReadWriteLock.BUSY_WAIT_ITERS):
            counter = memcache.get(lockKey)
            # counter is None --> ejected from memcache, or no writers
            # int(counter) <= 2**15 --> writers have all called memcache.decr
            if counter is None or int(counter) <= 2**15:
                break
            time.sleep(ReadWriteLock.BUSY_WAIT_ITER_SECS)
            self.context.logger.debug("Tried to acquire read lock '%s' %d times...", lockKey, i + 1)
        
        # FIXME: is there anything else that can be done? will work packages be lost? maybe queue another task
        #        to sweep up later?
        if i >= (ReadWriteLock.BUSY_WAIT_ITERS - 1): # pylint: disable-msg=W0631
            self.context.logger.critical("Gave up waiting for all fan-in work items with read lock '%s'.", lockKey)
            acquired = False
            if raiseOnFail:
                raise FanInReadLockFailureRuntimeError(nextEvent, 
                                                       self.context.machineName, 
                                                       self.context.currentState.name, 
                                                       self.context.instanceName)
        
        return acquired
    
class RunOnceSemaphore( object ):
    """ A object used to enforce run-once semantics """
    
    def __init__(self, semaphoreKey, context, obj=None):
        """ ctor 
        
        @param logger: a logging module or object
        """
        self.semaphoreKey = semaphoreKey
        if context is None:
            self.logger = logging
        else:
            self.logger = context.logger
        self.obj = obj

    def writeRunOnceSemaphore(self, payload=None, transactional=True):
        """ Writes the semaphore
        
        @return: a tuple of (bool, obj) where the first arg is True if the semaphore was created and work 
                 can continue, or False if the semaphore was already created, and the caller should take action
                 the second arg is the payload used on initial creation.
        """
        assert payload # so that something is always injected into memcache
        
        # the semaphore is stored in two places, memcache and datastore
        # we use memcache for speed and datastore for 100% reliability
        # in case of memcache ejection
        
        # check memcache
        cached = memcache.get(self.semaphoreKey)
        if cached:
            if cached != payload:
                self.logger.critical("Run-once semaphore memcache payload write error.")
            return (False, cached)
        
        # check datastore
        def txn():
            """ lock in transaction to avoid races between Tasks """
            entity = _FantasmTaskSemaphore.get_by_key_name(self.semaphoreKey)
            if not entity:
                _FantasmTaskSemaphore(key_name=self.semaphoreKey, payload=payload).put()
                memcache.set(self.semaphoreKey, payload)
                return (True, payload)
            else:
                if entity.payload != payload:
                    self.logger.critical("Run-once semaphore datastore payload write error.")
                memcache.set(self.semaphoreKey, entity.payload) # maybe reduces chance of ejection???
                return (False, entity.payload)
                
        # and return whether or not the lock was written
        if transactional:
            return db.run_in_transaction(txn)
        else:
            return txn()
    
    def readRunOnceSemaphore(self, payload=None, transactional=True):
        """ Reads the semaphore
        
        @return: True if the semaphore exists
        """
        assert payload
        
        # check memcache
        cached = memcache.get(self.semaphoreKey)
        if cached:
            if cached != payload:
                self.logger.critical("Run-once semaphore memcache payload read error.")
            return cached
        
        # check datastore
        def txn():
            """ lock in transaction to avoid races between Tasks """
            entity = _FantasmTaskSemaphore.get_by_key_name(self.semaphoreKey)
            if entity:
                if entity.payload != payload:
                    self.logger.critical("Run-once semaphore datastore payload read error.")
                return entity.payload
            
        # return whether or not the lock was read 
        if transactional:
            return db.run_in_transaction(txn)
        else:
            return txn()
    