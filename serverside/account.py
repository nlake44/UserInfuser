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
# Server side script for ajax calls
# Gives user info and other client side info

import wsgiref.handlers
import cgi
import webapp2
from google.appengine.ext import db
from entities.users import *
from tools.xss import XssCleaner
import json

class AccountInfo(webapp2.RequestHandler):
  def get(self):
    resp = {"success":"false","error":"User not logged in"}
    resp_json = json.dumps(resp)
    self.response.out.write(resp_json)
    return

