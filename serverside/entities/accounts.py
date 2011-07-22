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

from serverside.constants import *
from serverside.entities.widgets import TrophyCase
from serverside.entities.widgets import Points
from serverside.entities.widgets import Rank
from serverside.entities.widgets import Milestones
from serverside.entities.widgets import Leaderboard
from serverside.entities.widgets import Notifier
json = simplejson

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
  password = db.StringProperty(required=True);
  isEnabled = db.StringProperty(required=True, choices=ACCOUNT_STATUS.RANGE_OF_VALUES)
  creationDate = db.DateTimeProperty(auto_now_add=True)
  modifiedDate = db.DateTimeProperty(auto_now=True)
  accountType = db.StringProperty(required=True, 
                                  choices=set(ACCOUNT_TYPES)) 
  paymentType = db.StringProperty(required=True, 
                                  choices=set(PAYMENT_TYPES))
  cookieKey = db.StringProperty(required=True)
  apiKey = db.StringProperty(required=True)

  trophyWidget = db.ReferenceProperty(required=True, reference_class=TrophyCase)
  pointsWidget = db.ReferenceProperty(required=True, reference_class=Points)
  rankWidget = db.ReferenceProperty(required=True, reference_class=Rank)
  notifierWidget = db.ReferenceProperty(reference_class=Notifier)
  milestoneWidget = db.ReferenceProperty(reference_class=Milestones)
  leaderWidget = db.ReferenceProperty(reference_class=Leaderboard)

  lastPayment = db.StringProperty()
  firstName = db.StringProperty()
  lastName = db.StringProperty()
  address = db.StringProperty()
  city = db.StringProperty()
  phoneNumber = db.StringProperty()
  state = db.StringProperty()
  country = db.StringProperty()
  comments = db.TextProperty()
  receiveMarketEmails = db.BooleanProperty()
  receiveAnalysisEmails = db.BooleanProperty()
  pointsTrackingPeriod = db.StringProperty(choices=set(["daily","weekly", "monthly"] ))
  lastPointsReset = db.DateTimeProperty()
  notifyOnPoints = db.BooleanProperty(default=True)
  # TODO do not use iconfinder's CDN, serve it up locally
  pointsImage = db.StringProperty(default="http://cdn4.iconfinder.com/data/icons/prettyoffice/128/add1-.png")
  loginImage = db.StringProperty(default="http://cdn1.iconfinder.com/data/icons/Hosting_Icons/128/secure-server-px-png.png")
