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
Created on Feb 5, 2011

@author: shan
'''
from serverside.constants import WEB_ADMIN_PARAMS
from serverside.entities import memcache_db
from serverside.tools import encryption
import logging
import urllib
import time


class Session:
 
  """
  Class that contains class methods that are utils for account admin sessions. 
  Also, instance methods for tracking sessions when needed. This includes setting
  cookie params, or other params (in case we want to use other methods state
  tracking like GET requet params).
  """ 

  def create_session(self, request, email, ssid, expiration):
    """
    Encrypt parameters, set valid in DB, set cookie on client
    """
    account = memcache_db.get_entity(email, "Accounts")
    if account != None:
      update_fields = {"cookieKey" : ssid}
      memcache_db.update_fields(email, "Accounts", update_fields)
    
      email_enc = encryption.des_encrypt_str(email)
      ssid_enc = encryption.des_encrypt_str(ssid)
      exp_enc = encryption.des_encrypt_str(expiration)
      
      import base64
      import string
      email_encoded = string.rstrip(base64.encodestring(email_enc), "\n")
      ssid_encoded = string.rstrip(base64.encodestring(ssid_enc), "\n")
      exp_encoded = string.rstrip(base64.encodestring(exp_enc), "\n")
  
      # the email will be set as the key so we can use it to look up in the DB
      request.response.headers.add_header("Set-Cookie", WEB_ADMIN_PARAMS.COOKIE_EMAIL_PARAM + "=" + email_encoded)
      request.response.headers.add_header("Set-Cookie", WEB_ADMIN_PARAMS.COOKIE_KEY_PARAM + "=" + ssid_encoded)
      request.response.headers.add_header("Set-Cookie", WEB_ADMIN_PARAMS.COOKIE_EXPIRATION + "=" + exp_encoded)
      
      """ Create a new session object and return it """
      self.email = email
      self.ssid = ssid
      self.expiration = expiration
      self.account = account
    
      return self
    else:
      return None

  def get_current_session(self, request):
    """
    Returns a session object if a session can be detected given the HTTP request.
    This may include sifting through cookie values, or request params.
    
    Args:
    request
    
    Returns:
    Session or None
    """
    quoted_email = request.request.cookies.get(WEB_ADMIN_PARAMS.COOKIE_EMAIL_PARAM)
    quoted_ssid = request.request.cookies.get(WEB_ADMIN_PARAMS.COOKIE_KEY_PARAM)
    quoted_exp = request.request.cookies.get(WEB_ADMIN_PARAMS.COOKIE_EXPIRATION)
    
    if quoted_email == "" or quoted_ssid == "" or quoted_exp == "" or quoted_email == None or quoted_ssid == None or quoted_exp == None:
      return None
    else:
      import base64
      try: 
        unquoted_email = base64.decodestring(quoted_email)
        unquoted_ssid = base64.decodestring(quoted_ssid)
        unquoted_exp = base64.decodestring(quoted_exp)
      
        decrypted_email = encryption.des_decrypt_str(unquoted_email)
        decrypted_ssid = encryption.des_decrypt_str(unquoted_ssid)
        decrypted_exp = encryption.des_decrypt_str(unquoted_exp)
      except:
        logging.error("Error decoding sesssion: UnicodeDecodeError: 'ascii' codec can't decode byte: ordinal not in range(128)")
        return None 
      """ Make sure that the session has not expired """
      now = time.time()
      if not decrypted_exp:
        decrypted_exp = 0
      exp = float(decrypted_exp)
      if(now < exp):
        """ Make sure that the session is still valid """
        account = memcache_db.get_entity(decrypted_email, "Accounts")
        if account != None and account.cookieKey == decrypted_ssid:
          """ Create a new session object and return it """
          self.email = decrypted_email
          self.ssid = decrypted_ssid
          self.expiration = decrypted_exp
          self.account = account
        else:
          return None
      else:
        return None
      return self

  def terminate(self):
    """
    Remove cookie_key from datastore
    """
    email = self.email
    if email != None and email != "":
      account = memcache_db.get_entity(self.email, "Accounts")
      if account != None:
        update_fields = {"cookieKey" : "nada" }
        memcache_db.update_fields(email, "Accounts", update_fields)
  
  def get_email(self):
    return self.email
  
  def get_ssid(self):
    return self.ssid
  
  def get_expiration(self):
    return self.expiration
  
  def get_account_entity(self):
    return self.account

    
