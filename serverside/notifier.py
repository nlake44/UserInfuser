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
from google.appengine.api import channel
from entities.accounts import Accounts
from entities.badges import *
from entities.users import *
from serverside import logs
from serverside import constants
from serverside.constants import TEMPLATE_PATHS
from serverside.session import Session
from tools.utils import account_login_required
from tools.xss import XssCleaner, XssCleaner
from serverside.dao import accounts_dao

import logging
import os
import json

def get_channel_token(user_ref):
  if not user_ref:
    return None
  token = channel.create_channel(user_ref.key().name())
  return token

def user_points(user_ref, points, title, acc):
  if not user_ref or not acc:
    return None
  try:
    image = acc.pointsImage
  except:
    acc.pointsImage = constants.IMAGE_PARAMS.POINTS_IMAGE
    accounts_dao.save(acc)
  diction = {'event':'notify_points',
             'user':user_ref.userid,
             'account':acc.key().name(),
             'points':points,
             'widget':'notifier',
             'is_api':'no',
             'details':"title: "+title,
             'success':'true'}
              
  message = {'note':"+" + str(points) + " Points", 'image': image, 'title': title}
  message = json.dumps(message)
  try:
    channel.send_message(user_ref.key().name(), message)
    logs.create(diction)  
  except channel.InvalidChannelClientIdError:
    diction['success'] = "false"
    logging.error("Bad Channel ID for acc %s and user %s"%(acc.key().name(), user_ref.key().name()))
    logs.create(diction)
    return  
  
def user_badge_award(user_ref, note, imglink, title, acc, badge_id):
  assert badge_id != None
  assert user_ref != None

  diction = {'event':'notify_badge',
             'user':user_ref.userid,
             'account':acc.key().name(),
             'badge':imglink,
             'widget':'notifier',
             'is_api':'no',
             'details':'note: '+note+", title: "+title,
             'badgeid': badge_id,
             'success':'true'}
  message = {'note':note, 'image': imglink, 'title': title}
  message = json.dumps(message)
  try:
    channel.send_message(user_ref.key().name(), message)
    logs.create(diction)
  except channel.InvalidChannelClientIdError:
    diction['success'] = "false"
    logging.error("Bad Channel ID for acc %s and user %s"%(acc.key().name(), user_ref.key().name()))
    logs.create(diction)
    return  
