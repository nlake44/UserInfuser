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
from google.appengine.api import users
from google.appengine.ext import db
from serverside import constants
from serverside.dao import accounts_dao
from serverside.entities.counter import APICountBatch
import base64
import datetime
import httplib
import logging
import os
import json 
import urllib
import webapp2

class AppsAuthToken(db.Model):
  value = db.StringProperty()
  appname = db.StringProperty()
  enabled = db.BooleanProperty()
  
def get_x_apps_token():
  aset = AppsAuthToken.all().filter('appname =', 'xapps')
  if not aset or (aset and not aset.get()):
    logging.info('Creating new xappstoken')
    token = AppsAuthToken(value='----', appname = 'xapps', enabled= False)
    token.save()
    return token
  else:
    return aset.get()

def x_app_auth_required(method):
  def auth(self, *args):
    if users.is_current_user_admin():
      method(self,*args)
      return
    
    headers = self.request.headers
    tokenr = headers.get('xapp-token')
    
    if not tokenr:
      logging.info('No xapp token provided')
      self.error(400)
      self.response.out.write('Unable to authenticate!')
      return
    
    token = get_x_apps_token()
    
    if not token:
      logging.error('No token found.. weird...')
      self.error(400)
      self.response.out.write('Unable to authenticate!')
      return
    
    if not token.enabled:
      logging.info('Token disabled')
      self.error(400)
      self.response.out.write('Unable to authenticate!')
      return
    
    if tokenr == token.value and token.enabled:
      method(self,*args)
    else:
      logging.info('Token mismatch.. ' + tokenr + ' ' + token.value)
      self.error(400)
      self.response.out.write('Unable to authenticate!')
  return auth

class SendXAppToken(webapp2.RequestHandler):
  def get(self):
    if users.is_current_user_admin():
      location = self.request.get('location')
      path = self.request.get('path')
      
      conn = httplib.HTTPSConnection(location) # <---- needs to be HTTPS!!!!
      
      params = urllib.urlencode({'xapptoken': get_x_apps_token()})
      conn.request('POST', path, params)
      
      data = conn.getresponse().read()
      
      logging.critical('Sent XAppToken to ' + location + path + ' and this is the response: ' + data)
      
      conn.close()
  
class Authenticate(webapp2.RequestHandler):
  """
  Authenticates user and password combo
  """
  @x_app_auth_required
  def post(self):
    username = self.request.get('email')
    password = self.request.get('password')
    
    logging.info("Authentication attempt from: " + username)
    
    entity = accounts_dao.authenticate_web_account(username, password)
    if not entity:
      self.error(400)

class AccountUsage(webapp2.RequestHandler):
  def get(self):
    self.post()
  """
  Returns UserInfuser API usage for user. Only username required.
  """
  @x_app_auth_required
  def post(self):
    username = self.request.get('email')
    
    accounts = None
    if not username:
      accounts = accounts_dao.get_all_accounts()
    else:
      entity = accounts_dao.get(username)
      if not entity:
        self.error(400)
        return
      accounts = []
      accounts.append(entity)
    
    alldata = {'usage':[]}
    ''' retrieve all usage information summary (just API calls) '''
    for acc in accounts:
      q = APICountBatch.all().filter("account_key =", acc.key().name())
      values = {"success": "true", "email" : acc.email}
      res = q.fetch(1000) 
      values['total'] = q.count() or 1
      monthsdict = {}
      for ii in res:
        monthyear = ii.date.strftime('%Y-%m')
        curr=monthsdict.get(monthyear)
        if not curr:
          curr = 0
        curr += int(ii.counter)
        monthsdict[monthyear] = curr
      values['months'] = monthsdict
      alldata['usage'].append(values)
    
    self.response.out.write(json.dumps(alldata))

app = webapp2.WSGIApplication([
  ('/accinfo/auth', Authenticate),
  ('/accinfo/usage', AccountUsage)], debug=constants.DEBUG)

