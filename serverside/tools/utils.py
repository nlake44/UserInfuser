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
Created on Jan 10, 2011

@author: shan
'''
from google.appengine.ext.webapp import template
from serverside.constants import TEMPLATE_PATHS
from serverside.session import Session
import re
import logging
import string
import random

def generate_random_string(length = 8):
  """ Will generate a random uppercase/number string for specified length """
  return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(length))

def camelcase_to_friendly_str(s):
  """
  Utility to convert camelcase string to a friend string.
  For example, camelcase_to_friendly_str("helloWorld") would return "Hello World"
  """
  if s == None or len(s) < 1:
    return None
  
  ret_str = ""
  j=0
  for i in range(len(s)):
    if str(s[i]).isupper():
      ret_str += s[j:i] + " "
      j=i
  ret_str += s[j:]
  
  import string
  ret_str = string.capitalize(ret_str[0]) + ret_str[1:]
  return ret_str
  

def validEmail(email):
  """Check to see if the string is formatted as a valid email address.
  """
  
  if len(email) > 7:
    if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
      return 1
    return 0

def account_login_required(handler_method):
  """
  Decorator to check if user is logged in. If user is not logged in they will be redirect to login screen.
  """

  def check_login(self, *args):
    if self.request.method != 'GET' and self.request.method != 'POST':
      self.response.out.write(template.render(TEMPLATE_PATHS.CONSOLE_LOGIN, None))
    else:
      user_session = Session().get_current_session(self)
      if user_session == None:
        self.response.out.write(template.render(TEMPLATE_PATHS.CONSOLE_LOGIN, None))  
      else:
        logging.info("LEGIT user session! Email: " + user_session.get_email())
        handler_method(self, *args)
        
  return check_login

def format_integer(number):
  s = '%d' % number
  groups = []
  while s and s[-1].isdigit():
      groups.append(s[-3:])
      s = s[:-3]
  return s + ','.join(reversed(groups))

