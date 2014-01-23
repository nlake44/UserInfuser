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
import cgi
import logging
import os
import wsgiref.handlers
import urllib
import webapp2
from google.appengine.api import urlfetch
from serverside import constants
from serverside import environment
from serverside.dao import passphrase_dao 
from serverside.dao import accounts_dao
from serverside.dao import users_dao
from serverside.dao import widgets_dao 
from google.appengine.api import taskqueue

def check_or_create_anonymous_user(acc_ref):
  """ Create an anonymous users if needed """
  return users_dao.get_or_create_user(acc_ref.key().name(), constants.ANONYMOUS_USER, acc_ref)

def has_milestone_widget(acc_ref):
  """ Adds a milestone widget if needed """
  widget = None
  try:
    widget = widgets_dao.get_widget_for_account(acc_ref, "Milestones")
  except:
    logging.error("Unable to get Milestone widget for account " + acc_ref.key().name() + " will have to create it")   
  if not widget:
    logging.error("No Milestone widget for account " + acc_ref.key().name() + " will have to create it")   
    widget = widgets_dao.add_milestones(acc_ref)
  return widget

def groom_account(email):
  """ 
      Check the account and make sure accounts are updated with newest 
      parameters, widgets, users, etc
  """
  acc = accounts_dao.get(email)
  if not acc:
    logging.error("Unable to locate account ref for " + str(email))
    return 

  if not check_or_create_anonymous_user(acc):
    logging.error("Unable to get/create anonymous user for " + str(email))
    return 

  if not has_milestone_widget(acc):
    logging.error("Unable to get/create milestone wildget for" + str(email))
    return 

class UpdateAccount(webapp2.RequestHandler):
  def post(self):
    email = self.request.get('email') 
    updatesecret = self.request.get('key') 
    official_update_secret = passphrase_dao.get_update_secret()    
    if updatesecret != official_update_secret:
      logging.error("Logging: Bad update secret: %s vs %s"%(updatesecret, official_update_secret))
      return
    groom_account(email)

app = webapp2.WSGIApplication([
  (constants.UPDATE.PATH, UpdateAccount)
], debug=constants.DEBUG)

def __url_async_post(url, argsdic):
  # This will not work on the dev server for GAE, dev server only uses
  # synchronous calls, unless the SDK is patched, or using AppScale
  #rpc = urlfetch.create_rpc(deadline=30)
  #urlfetch.make_fetch_call(rpc, url, payload=urllib.urlencode(argsdic), method=urlfetch.POST)
  taskqueue.add(url=url, params=argsdic)

def full_path(relative_url):
  if environment.is_dev():
    return constants.DEV_URL + constants.UPDATE.PATH
  else:
    return constants.PRODUCTION_URL + constants.UPDATE.PATH

def update_account(email):
  diction = {}
  diction['key'] = passphrase_dao.get_update_secret()    
  diction['email'] = email
  __url_async_post(constants.UPDATE.PATH, diction)

"""
def main():
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
"""
