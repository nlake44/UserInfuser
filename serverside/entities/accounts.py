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

import json
from serverside.constants import *
from serverside.entities.widgets import TrophyCase
from serverside.entities.widgets import Points
from serverside.entities.widgets import Rank
from serverside.entities.widgets import Milestones
from serverside.entities.widgets import Leaderboard
from serverside.entities.widgets import Notifier

"""
Class: 
  Account
Description:
  The accounts class is a primary user of the application.
  Email is required.
  The key to an account is always the email account
  The cookieKey is created at the time of creation.
  For proper scaling we must update the account as less as possible, given
  that writes max out at about 20/sec in GAE. We can do this via memcache.
  Do puts to logs/journals for login information. 
"""
class Accounts(db.Model):
  email = db.EmailProperty(required=True)
  password = db.StringProperty(required=True, indexed=False);
  isEnabled = db.StringProperty(required=True, choices=ACCOUNT_STATUS.RANGE_OF_VALUES)
  creationDate = db.DateTimeProperty(auto_now_add=True, indexed=False)
  modifiedDate = db.DateTimeProperty(auto_now=True, indexed=False)
  accountType = db.StringProperty(required=True, 
                                  choices=set(ACCOUNT_TYPES), indexed=False) 
  paymentType = db.StringProperty(required=True, 
                                  choices=set(PAYMENT_TYPES), indexed=False)
  cookieKey = db.StringProperty(required=True, indexed=False)
  apiKey = db.StringProperty(required=True)

  trophyWidget = db.ReferenceProperty(required=True, reference_class=TrophyCase)
  pointsWidget = db.ReferenceProperty(required=True, reference_class=Points)
  rankWidget = db.ReferenceProperty(required=True, reference_class=Rank)
  notifierWidget = db.ReferenceProperty(reference_class=Notifier)
  milestoneWidget = db.ReferenceProperty(reference_class=Milestones)
  leaderWidget = db.ReferenceProperty(reference_class=Leaderboard)

  lastPayment = db.StringProperty(indexed=False)
  firstName = db.StringProperty(indexed=False)
  lastName = db.StringProperty(indexed=False)
  address = db.StringProperty(indexed=False)
  city = db.StringProperty(indexed=False)
  phoneNumber = db.StringProperty(indexed=False)
  state = db.StringProperty(indexed=False)
  country = db.StringProperty(indexed=False)
  comments = db.TextProperty(indexed=False)
  receiveMarketEmails = db.BooleanProperty(indexed=False)
  receiveAnalysisEmails = db.BooleanProperty(indexed=False)
  pointsTrackingPeriod = db.StringProperty(choices=set(["daily","weekly", "monthly"] ), indexed=False)
  lastPointsReset = db.DateTimeProperty(indexed=False)
  notifyOnPoints = db.BooleanProperty(default=True, indexed=False)
  # TODO do not use iconfinder's CDN, serve it up locally
  pointsImage = db.StringProperty(default="http://cdn4.iconfinder.com/data/icons/prettyoffice/128/add1-.png", indexed=False)
  loginImage = db.StringProperty(default="http://cdn1.iconfinder.com/data/icons/Hosting_Icons/128/secure-server-px-png.png", indexed=False)
