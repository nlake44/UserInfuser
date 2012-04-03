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
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from serverside import constants
from serverside.dao import accounts_dao
from serverside.entities.counter import APICountBatch
import base64
import datetime
import simplejson



class Authenticate(webapp.RequestHandler):
  """
  Authenticates user and password combo
  """
  def post(self):
    encodeduser = self.request.get('email')
    encodedpass = self.request.get('password')
    
    username = base64.decodestring(encodeduser)
    password = base64.decodestring(encodedpass)
    
    entity = accounts_dao.authenticate_web_account(username, password)
    if not entity:
      self.error(400)

class AccountUsage(webapp.RequestHandler):
  """
  Returns UserInfuser API usage for user. Username and password required.
  """
  def post(self):
    encodeduser = self.request.get('email')
    encodedpass = self.request.get('password')
    
    username = base64.decodestring(encodeduser)
    password = base64.decodestring(encodedpass)
    
    entity = accounts_dao.authenticate_web_account(username, password)
    if not entity:
      self.error(400)
      return
    
    ''' retrieve all usage information summary (just API calls) '''
    
    q = APICountBatch.all().filter("account_key =", entity.key().name())
    values = {"success": "true"}
    res = q.fetch(1000) 
    values['total'] = q.count() or 1
    values['entry'] = []
    for ii in res:
      ent = {'date':ii.date.strftime("%Y-%m-%d"),
             'count':str(ii.counter)}
      values['entry'].append(ent)
    else:
      ent = {'date':datetime.datetime.now().strftime("%Y-%m-%d"),
             'count':"0"}
      values['entry'].append(ent)
    
    self.response.out.write(simplejson.dumps(values))

application = webapp.WSGIApplication([
  ('/accinfo/auth', Authenticate),
  ('/accinfo/usage', AccountUsage)], debug=constants.DEBUG)

def main():
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
