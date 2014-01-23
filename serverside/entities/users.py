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
import logging
import hashlib
import datetime
from google.appengine.ext import db
from serverside.entities.accounts import Accounts
from serverside import constants
import json
class Users(db.Model):
  userid = db.StringProperty(required=True)
  isEnabled = db.StringProperty(required=True, choices=set(["yes","no"]))
  creationDate = db.DateTimeProperty(auto_now_add=True, indexed=False)
  modifiedDate = db.DateTimeProperty(auto_now=True, indexed=False)
  accountRef = db.ReferenceProperty(reference_class=Accounts, required=True)
  points = db.IntegerProperty(default=0)
  rank = db.IntegerProperty(default=constants.NOT_RANKED)
  last_time_ranked = db.DateTimeProperty(indexed=False)
  profileName = db.StringProperty(default="Anonymous", indexed=False)
  profileLink = db.TextProperty(indexed=False)
  profileImg = db.TextProperty(default="http://i.imgur.com/hsDiZ.jpg", indexed=False)
  userNotes = db.TextProperty(indexed=False)
  tags = db.StringProperty()
