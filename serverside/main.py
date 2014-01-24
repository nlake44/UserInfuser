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
import wsgiref.handlers
import cgi
from google.appengine.ext.webapp import template
from serverside.console import Console
from serverside.entities.users import Users
from serverside.account import Accounts
from serverside.signup import NewsLetterSignUp
from serverside.signup import SignUp
from serverside.signin import SignIn
from serverside.logout import LogOut
from serverside.badge import UploadBadge
from serverside.badge import DownloadBadge 
from serverside.badge import SeeTheme
from serverside.analytics import GetAnalytics
from serverside.analytics import RunAnalytics
from serverside import constants
import webapp2
from google.appengine.ext import db
from google.appengine.api import users
import logging
import os
from serverside.analytics import *

class IndexPage(webapp2.RequestHandler):
  def get(self):
    self.redirect('/html/signup.html')

class HelloWorld(webapp2.RequestHandler):
  def get(self):
    self.response.out.write("hi!")

app = webapp2.WSGIApplication([
  ('/', IndexPage),
  ('/account', Accounts),
  ('/login', SignIn),
  ('/signup', SignUp),
  ('/logout', LogOut),
  ('/badge/u', UploadBadge),
  ('/badge/d', DownloadBadge),
  ('/badge/t', SeeTheme),
  ('/newslettersignup',NewsLetterSignUp),
  ('/hello', HelloWorld),
  ('/runanalytics', RunAnalytics),
  ('/getanalytics', GetAnalytics),
], debug=constants.DEBUG)

"""
def main():
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
"""
