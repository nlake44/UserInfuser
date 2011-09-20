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
import datetime
from google.appengine.ext import db
from serverside import constants

class APICountBatch(db.Model):
  date = db.DateTimeProperty()
  account_key = db.StringProperty()
  counter = db.IntegerProperty(default=0, indexed=False)

class PointBatch(db.Model):
  date = db.DateTimeProperty()
  account_key = db.StringProperty()
  counter = db.IntegerProperty(default=0, indexed=False)

class BadgePointsBatch(db.Model):
  date = db.DateTimeProperty()
  account_key = db.StringProperty()
  badgeid = db.StringProperty()
  counter = db.IntegerProperty(default=0, indexed=False)

class BadgeBatch(db.Model):
  date = db.DateTimeProperty()
  account_key = db.StringProperty()
  badgeid = db.StringProperty()
  counter = db.IntegerProperty(default=0, indexed=False)
