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
from django.utils import simplejson
from serverside.entities.accounts import Accounts
from serverside import constants
json = simplejson

class Users(db.Model):
  userid = db.StringProperty(required=True)
  isEnabled = db.StringProperty(required=True, choices=set(["yes","no"]))
  creationDate = db.DateTimeProperty(auto_now_add=True)
  modifiedDate = db.DateTimeProperty(auto_now=True)
  accountRef = db.ReferenceProperty(reference_class=Accounts, required=True)
  points = db.IntegerProperty(default=0)
  rank = db.IntegerProperty(default=constants.NOT_RANKED)
  last_time_ranked = db.DateTimeProperty()
  profileName = db.StringProperty(default="Anonymous")
  profileLink = db.StringProperty()
  profileImg = db.StringProperty(default="http://i.imgur.com/hsDiZ.jpg")
  userNotes = db.StringProperty()
  tags = db.StringProperty()
