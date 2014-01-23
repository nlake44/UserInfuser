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
import webapp2
from google.appengine.ext.webapp import template
from serverside.constants import WEB_ADMIN_PARAMS, TEMPLATE_PATHS
from serverside.entities import memcache_db
from serverside.session import Session
from serverside.dao import accounts_dao
from serverside import update_account 
import logging
import time
import uuid


class SignIn(webapp2.RequestHandler):

  def post(self):
    """Get the username and password, hash password. Authenticate, make sure account is enabled then redirect to account page. """
    email = self.request.get("email")
    password = self.request.get("password")
    
    logging.info("Attempted log in attempt, email: " + email)
    
    template_values = {'error': "error"}
    if email != None and email != "" and password != None and password != "":
      entity = accounts_dao.authenticate_web_account(email, password)
      if entity:
        update_account.update_account(entity.key().name())
        Session().create_session(self, email, str(uuid.uuid4()), str(time.time() + WEB_ADMIN_PARAMS.VALID_FOR_SECONDS))
        self.redirect("/adminconsole")
      else:
        self.response.out.write(template.render(TEMPLATE_PATHS.CONSOLE_LOGIN, template_values))
    else:
      self.response.out.write(template.render(TEMPLATE_PATHS.CONSOLE_LOGIN, template_values))
