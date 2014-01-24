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
"""
Author: Navraj Chohan
Description:
There are three badge types: The image, the template, and an instance
"""

import logging
import hashlib
import datetime
from accounts import Accounts
from users import Users

from google.appengine.ext import db
from google.appengine.ext.blobstore import blobstore

import json
BOOLEAN = ["yes", "no"]
TYPES = ["free", "basic", "premium"]
STYPE = ["blob", "db"]
PERMISSION = ["private", "public"]

"""
Class: BadgeImage
Description: Stores the image of the badge
Attributes:
  image: the image binary
  permissions: pub or private
  creator: Who created it 
Notes:This instance type is only for testing purposes. 
      Actual images are stored using blobstore
"""
class BadgeImage(db.Model): 
  image = db.BlobProperty(required=True)  
  permissions = db.StringProperty(required=True, choices=set(PERMISSION))
  creator = db.ReferenceProperty(reference_class=Accounts, required=True)
  imgType = db.StringProperty(required=True, choices=set(['jpg','gif','png', 'gif']), indexed=False)
  creationDate = db.DateTimeProperty(auto_now_add=True, indexed=False)
  modifiedDate = db.DateTimeProperty(auto_now=True, indexed=False)

"""
Class: Badges
Description: A badge type
Attributes:
  name: What the badge is called
  description: A brief explanation about the badge
  altText: The alt text you see in the browser
  setType: The pricing level
  isEnabled
  creationDate
  creator: A reference to the account who created this type
  tags: Tags by the owner (or everyone, if public)
  permissions: Permission, if we allow sharing
  blobKey: A reference to the image of this type
"""
class Badges(db.Model):
  name = db.StringProperty(required=True)
  description = db.TextProperty(required=True)
  altText = db.TextProperty(required=True)
  setType = db.TextProperty(required=True, choices=set(TYPES))
  isEnabled = db.StringProperty(required=True, choices=set(BOOLEAN))
  creationDate = db.DateTimeProperty(auto_now_add=True, indexed=False)
  modifiedDate = db.DateTimeProperty(auto_now=True, indexed=False)
  creator = db.ReferenceProperty(reference_class=Accounts, required=True)
  tags = db.StringProperty()
  permissions = db.StringProperty(required=True, choices=set(PERMISSION))
  storageType = db.StringProperty(required=True, choices=set(STYPE), indexed=False)
  # This if you want to make the badge clickable, and route to a resource
  # or secret link, etc
  resourceLink = db.LinkProperty(indexed=False)
  downloadLink = db.LinkProperty(indexed=False)
  # a reference key to the object stored into the blobstore
  blobKey =  blobstore.BlobReferenceProperty()
  imageKey = db.ReferenceProperty(reference_class=BadgeImage)
  # Uploaded files in static images of badges
  filePath = db.StringProperty(indexed=False)
  theme = db.StringProperty()
  
"""
Class: BadgeInstance
Description: An instance of a badge which has been given to a user
Attributes:
  badgeRef: A reference to the type of badge
"""
class BadgeInstance(db.Model): 
  badgeRef = db.ReferenceProperty(reference_class=Badges, required=True)
  userRef = db.ReferenceProperty(reference_class=Users, required=True)
  awarded = db.StringProperty(required=True, choices=set(BOOLEAN))
  permissions = db.StringProperty(required=True, choices=set(PERMISSION))
  creationDate = db.DateTimeProperty(auto_now_add=True, indexed=False)
  awardDateTime = db.DateTimeProperty(indexed=False)
  awardDate = db.DateProperty(indexed=False)
  modifiedDate = db.DateTimeProperty(auto_now=True, indexed=False)
  instanceRegistrationDate = db.DateTimeProperty(auto_now=True, indexed=False)
  pointsRequired = db.IntegerProperty(default=9999999999, indexed=False)
  pointsEarned = db.IntegerProperty(default=0, indexed=False)
  expirationDate = db.DateTimeProperty(indexed=False)
  resource = db.LinkProperty(indexed=False)
  reason = db.StringProperty(indexed=False)
  downloadLink = db.LinkProperty(indexed=False)
