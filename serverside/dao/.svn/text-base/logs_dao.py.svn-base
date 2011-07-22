# Copyright (C) 2011, CloudCaptive
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
'''
Created on Feb 24, 2011

DAO methods for logging. Calls paths for logging events.

@author: Raj
'''
from serverside.entities.logs import Logs
from google.appengine.api import urlfetch

import logging
import random
import string
def gen_random(length):
  return ''.join(random.choice(string.letters) for i in xrange(length))

def save_log(diction):
  if "event" not in diction:
    logging.error("No event type in log")
    return
  key = gen_random(20)
  newlog = Logs(key_name=key, event=diction['event'])
  props = newlog.properties()
  for ii in diction:
    if ii in props:
       setattr(newlog, ii, diction[ii])
  newlog.put()
