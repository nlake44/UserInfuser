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
""" Author: Navraj Chohan
    Description: The server side API implementation of UI.
"""
from __future__ import with_statement
  
import os
import wsgiref.handlers
import cgi
import locale
import webapp2
from serverside.entities.users import Users
from serverside.entities.accounts import Accounts
from serverside.entities.badges import Badges
from serverside.entities.badges import BadgeImage
from serverside.entities.badges import BadgeInstance
from serverside.entities.widgets import Leaderboard
from serverside.entities.widgets import Rank
from serverside.entities.widgets import Points
from serverside.entities.widgets import Notifier
from serverside.entities.widgets import TrophyCase
from serverside.entities.widgets import Milestones
from serverside.tools.utils import format_integer
from serverside.dao import badges_dao
from serverside.dao import accounts_dao
from serverside.dao import users_dao
from serverside.dao import widgets_dao
from serverside import environment
from serverside import notifier
from serverside import logs
from google.appengine.ext import db
from google.appengine.api import urlfetch
from google.appengine.ext.webapp import template
from google.appengine.api import channel
from google.appengine.api import files
from google.appengine.ext import blobstore
from serverside import constants 
from serverside.tools.xss import XssCleaner
import json

import hashlib
import time
import datetime
import logging
import traceback
DEBUG = constants.DEBUG
DISABLE_LOGGING = False
DISABLE_TIMING = True
"""
How keys are created for each type of entity:
User: sha1(account_id + '-' + user_id)
Badge: creatoremail + '-' badgename + '-' + badgetheme + '-' + permissions
BadgeInstance: user_id + '-' + badge_key
The dao interface should have a create key function for each
"""
def debug(msg):
  if DISABLE_LOGGING:
    return 
  if DEBUG:
    frame = traceback.extract_stack(limit=1)[0]
    filename, line_number, name, text = frame
    logging.info('DEBUG, File "%s", line %d, in %s: %s' % (filename, line_number, name, msg))
  
def error(msg):
  if DISABLE_LOGGING:
    return 
  frame = traceback.extract_stack(limit=1)[0]
  filename, line_number, name, text = frame
  logging.error('ERROR, File "%s", line %d, in %s: %s' % (filename, line_number, name, msg))

def timing(start):
  if DISABLE_TIMING:
    return 
  end = time.time()
  frame = traceback.extract_stack(limit=1)[0]
  filename, line_number, name, text = frame
  msg = str(start)
  msg += str("," + str(end) + "," + str(end - start))
  logging.info('TIMING, File "%s", line %d, in %s: %s' % (filename, line_number, name, msg))

def get_top_users(acc_ref):
  if not acc_ref:
    error("Unable to get users because of missing account ref") 
    return None
  result = db.GqlQuery("SELECT * FROM Users WHERE accountRef=:1 ORDER BY points DESC LIMIT " + constants.TOP_USERS, acc_ref)
  filtered = []
  for index,ii in enumerate(result):
    delete_index = -1
    try:
      if ii.profileImg == None or ii.profileImg == "":
        ii.profileImg = constants.IMAGE_PARAMS.USER_AVATAR
    except:
      ii.profileImg = constants.IMAGE_PARAMS.USER_AVATAR
    if ii.userid != constants.ANONYMOUS_USER:
      if not ii.profileName:
        ii.profileName = "Anonymous"
      filtered.append(ii) 
  return filtered

def calculate_rank(user_ref, acc_ref):
  rank = constants.NOT_RANKED
  if not user_ref or not acc_ref:
    #error("Unable to cal rank because of missing user or account ref")
    return rank

  if user_ref.rank:
    rank = user_ref.rank  

  last_ranking = user_ref.last_time_ranked
  current_time = datetime.datetime.now()
  recalculate = True
  if last_ranking:
    recalculate = (current_time - last_ranking) > datetime.timedelta(minutes=10)
     
  # Do not calculate rank unless its been 10 minutes since last time
  if recalculate:
    result = db.GqlQuery("SELECT __key__ FROM Users WHERE accountRef=:1 ORDER BY points DESC LIMIT " + constants.NUMBER_RANKED, acc_ref)
    counter = 1
    is_ranked = False
    for ii in result:
      if ii.name() == user_ref.key().name():
        is_ranked = True
        break 
      else:
        counter += 1
    if is_ranked:
      user_ref.rank = counter
      rank = counter
    else:
      user_ref.rank = constants.NOT_RANKED
    
    user_ref.last_time_ranked = current_time
    user_key = user_ref.key().name()
    try:
      users_dao.save_user(user_ref, user_key)
    except:
      error("Error getting user with key %s"%user_key)
  return rank

def success_ret():
  ret = {'status':'success'}
  ret = json.dumps(ret)
  return ret

def db_error():
  ret = {'status':'failed',
        'errcode':constants.API_ERROR_CODES.INTERNAL_ERROR,
        'error':'Database error'} 
  ret = json.dumps(ret)
  return ret 
    
def auth_error():
  ret = {'status':'failed',
         'errcode':constants.API_ERROR_CODES.NOT_AUTH,
         'error':'Permission denied'} 
  ret = json.dumps(ret)
  return ret 

def bad_args():
  ret = {'status':'failed',
         'errcode':constants.API_ERROR_CODES.BAD_ARGS,
         'error':'Number of points is not an integer'} 
  ret = json.dumps(ret)
  return ret 

def bad_user():
  ret = {'status':'failed',
         'errcode':constants.API_ERROR_CODES.BAD_USER,
         'error':'Invalid user provided'}
  ret = json.dumps(ret)
  return ret 

def badge_error():
  ret = {'status':'failed',
         'errcode':constants.API_ERROR_CODES.BADGE_NOT_FOUND,
         'error':'Check your badge id'} 
  ret = json.dumps(ret)
  return ret

def user_error():
  ret = {'status':'failed',
         'errcode':constants.API_ERROR_CODES.USER_NOT_FOUND,
         'error':'User was not found'} 
  ret = json.dumps(ret)
  return ret


class API_1_Status(webapp2.RequestHandler):
  def post(self):
    start = time.time()
    self.response.out.write(success_ret())
    timing(start)
  def get(self):
    start = time.time()
    self.response.out.write(success_ret())
    timing(start) 

class API_1_GetUserData(webapp2.RequestHandler):
  def post(self):
    start = time.time()
    api_key = self.request.get('apikey')
    account_id = self.request.get('accountid')
    user_id = self.request.get('userid')
    user_key = users_dao.get_user_key(account_id, user_id)
    acc = accounts_dao.authorize_api(account_id, api_key)

    logdiction = {'event':'getuserdata', 
                  'api': 'get_user_data',
                  'is_api':'yes',
                  'user':user_id,
                  'account':account_id,
                  'success':'true',
                  'ip':self.request.remote_addr}
    if not acc:
      logdiction['success'] = 'false'
      logdiction['details'] = auth_error()
      logs.create(logdiction)
      self.response.out.write(auth_error())
      return 

    user_ref = users_dao.get_user(account_id, user_id)
    if not user_ref:
      logdiction['success'] = 'false'
      logdiction['details'] = user_error()
      logs.create(logdiction)
      error("User for account %s, %s not found"%(account_id, user_id))
      self.response.out.write(user_error())
      return 

    badges = badges_dao.get_user_badges(user_ref)
    badge_keys = []
    badge_detail = []

    # get the badge image link
    for b in badges:
      if b.awarded == "yes":
        bid = badges_dao.get_badge_id_from_instance_key(b.key().name())
        badge_keys.append(bid)
        
        # add badge detail
        try:
          badgeobj = b.badgeRef
          badge_detail.append({'id':bid,
                               'name': badgeobj.name,
                               'description': badgeobj.description,
                               'theme': badgeobj.theme,
                               'awarded': str(b.awardDateTime),
                               'downloadlink' : b.downloadLink})
        except:
          logging.error('Failed to add badge detail. Badge id: ' + bid)
        
        
    ret = {"status":"success",
           "user_id":user_ref.userid,
           "is_enabled":user_ref.isEnabled,
           "creation_date":str(user_ref.creationDate),
           "points":user_ref.points,
           "profile_name": user_ref.profileName,
           "profile_link": user_ref.profileLink,
           "profile_img": user_ref.profileImg,
           "badges": badge_keys,
           "badges_detail":badge_detail}
    logs.create(logdiction)
    self.response.out.write(json.dumps(ret)) 
    timing(start) 

class API_1_UpdateUser(webapp2.RequestHandler):
  def post(self):
    start = time.time()
    clean = XssCleaner()
    api_key = self.request.get('apikey')
    account_id = self.request.get('accountid')
    new_user_id = self.request.get('userid')
    # Anything that can possibly be rended should be cleaned 
    profile_link = self.request.get('profile_link')
    if profile_link != "" and not profile_link.startswith('http://'):
      profile_link = "http://" + profile_link

    # We can't clean it because it will not render if embedded into a site
    # Be wary of doing any queries with this data
    #profile_link = clean.strip(profile_link)
    profile_img = self.request.get('profile_img') 
    if profile_img != "" and  not profile_img.startswith('http://'):
      profile_img = "http://" + profile_img

    #profile_img = clean.strip(profile_img)
    profile_name = self.request.get('profile_name')
    profile_name = clean.strip(profile_name)
    logdiction = {'event':'loginuser', 
                  'api': 'update_user',
                  'is_api':'yes',
                  'ip':self.request.remote_addr,
                  'user':new_user_id,
                  'account':account_id,
                  'success':'true'}
    if not account_id or not new_user_id or not api_key:
      self.response.out.write(bad_args())
      logdiction['success'] = 'false'
      logdiction['details'] = bad_args()
      logs.create(logdiction)
      return

    acc = accounts_dao.authorize_api(account_id, api_key)
    if not acc:
      self.response.out.write(auth_error())
      logdiction['success'] = 'false'
      logdiction['details'] = auth_error()
      logs.create(logdiction)
      return 

    # Create a new user
    user_key = users_dao.get_user_key(account_id, new_user_id)

    #Update
    user_ref = users_dao.get_user_with_key(user_key)
    if user_ref:
      dict = {}
      update = False
      if profile_link and profile_link != user_ref.profileLink: 
        dict["profileLink"] = profile_link
        update = True
      if profile_img and profile_img != user_ref.profileImg: 
        dict["profileImg"] = profile_img
        update = True
      if profile_name and profile_name != user_ref.profileName: 
        dict["profileName"] = profile_name
        update = True
      if update: 
        logdiction['event'] = 'updateuser'
        try:
          users_dao.update_user(user_key, dict, None)
        except:
          logdiction['success'] = 'false'
          logdiction['details'] = db_error()
          logs.create(logdiction)
          self.response.out.write(db_error())
          error("Error updating user with id %s"%new_user_id)
          return  

      logs.create(logdiction)

      self.response.out.write(success_ret())
      timing(start)
      return  

    if not profile_img:   
      profile_img = constants.IMAGE_PARAMS.USER_AVATAR

    new_user = Users(key_name=user_key,
                     userid=new_user_id,
                     isEnabled="yes",
                     accountRef=acc,
                     profileName=profile_name,
                     profileLink=profile_link,
                     profileImg=profile_img)
    logdiction['event'] = 'createuser'
    try:
      users_dao.save_user(new_user, user_key)
    except:
      logdiction['success'] = 'false'
      logdiction['details'] = db_error()
      logs.create(logdiction)
      self.response.out.write(db_error())
      error("Error getting user with key %s"%user_key)
      return  

    logs.create(logdiction)
    self.response.out.write(success_ret())
    timing(start)
    return 

  def get(self):
    self.redirect('/html/404.html')
    return 

class API_1_AwardBadgePoints(webapp2.RequestHandler):
  def post(self):
    start = time.time()

    api_key = self.request.get('apikey')
    account_id = self.request.get('accountid')
    user_id = self.request.get('userid')
    badge_ref_id = self.request.get('badgeid')
    how_to_get_badge = self.request.get('how')
    points = self.request.get('pointsawarded')
    points_needed = self.request.get('pointsrequired')
    reason = self.request.get('reason') 
    logdiction = {'event':'awardbadgepoints', 
                  'api':'award_badge_points',
                  'user':user_id,
                  'is_api':'yes',
                  'ip':self.request.remote_addr,
                  'account':account_id,
                  'badgeid':badge_ref_id,
                  'points':points,
                  'success':'true'}
    try:
      points = int(points)
      points_needed = int(points_needed)
    except:
      logdiction['success'] = 'false'
      logdiction['details'] = "The number of points was not a number"
      logs.create(logdiction)
      self.response.out.write(bad_args())
      error("Account %s -- Bad value for points awarded \
                    %s or points needed %s"\
                    %(account_id, points, points_needed ))
      return

    if not reason:
      reason = ""

    # Get the account 
    acc = accounts_dao.authorize_api(account_id, api_key)
    if not acc:
      logdiction['success'] = 'false'
      logdiction['details'] = auth_error()
      logs.create(logdiction)
      self.response.out.write(auth_error())
      return 

    # Get the Badge Type (used as a reference for the instances) 
    # Do this before getting/creating user
    badge_key = badges_dao.get_key_from_badge_id(account_id, badge_ref_id)
    if not badge_key:
      logdiction['success'] = 'false'
      logdiction['details'] = badge_error()
      logs.create(logdiction)
      self.response.out.write(badge_error())
      error("Badge not found with key %s"%badge_ref_id)
      return  

    # Get the user, create if it does not exist
    user_ref = users_dao.get_or_create_user(account_id, user_id, acc)
    if not user_ref:
      logdiction['success'] = 'false'
      logdiction['details'] = db_error()
      logs.create(logdiction)
      self.response.out.write(db_error())
      return  
  
    badge_ref = badges_dao.get_badge(badge_key) 
    if not badge_ref:
      logdiction['success'] = 'false'
      logdiction['details'] = badge_error()
      logs.create(logdiction)
      ret = badge_error()
      self.response.out.write(ret)
      return  

    badge_instance_key = badges_dao.get_badge_instance_key(badge_key, user_id)
    badge_instance_ref = badges_dao.get_badge_instance(badge_instance_key)

    if not reason:
      reason = badge_ref.description
    link = badge_ref.downloadLink

    if not badge_instance_ref:
      # Create a new badge with 0 points
      isawarded = "no"
      if points >= points_needed:
        isawarded = "yes" 
      perm = badges_dao.get_badge_key_permission(badge_ref_id)
      new_badge_instance = badges_dao.create_badge_instance(
                                       badge_instance_key,
                                       badge_ref,
                                       user_ref,
                                       isawarded,
                                       points,
                                       points_needed,
                                       perm,
                                       link,
                                       reason)
      if isawarded == "yes":
        notifier.user_badge_award(user_ref, "Badge Awarded", link, reason, acc, badge_ref_id)
        logdiction['event'] = 'badgeawarded'
    else: 
      isawarded = "no"
      points_thus_far = badge_instance_ref.pointsEarned
      if points:
        points_thus_far += points
      incr_args = {"pointsEarned":points}
      reg_args = {}
      # Update the following if its changed
      if badge_instance_ref.pointsRequired != points_needed:
        reg_args["pointsRequired"] = points_needed

      if badge_instance_ref.pointsEarned < points_needed and \
              points_thus_far >= points_needed:
        notifier.user_badge_award(user_ref, "Badge Awarded", link, reason, acc, badge_ref_id)
        logdiction['event'] = 'badgeawarded'

      if points_thus_far >= points_needed:
        reg_args["awarded"] = "yes"
        isawarded = "yes"
      try:
        ret = badges_dao.update_badge_instance(badge_instance_key, 
                                reg_args, incr_args)
        if not ret:
          raise
      except:
        error("Unable to update badge instance with key %s"%\
              badge_instance_key)
        self.response.out.write(db_error())
        return
    logs.create(logdiction)
    ret = {"status":"success",
           "badge_awarded":isawarded}
    self.response.out.write(json.dumps(ret))
    timing(start)
    return  

  def get(self):
    self.redirect('/html/404.html')


class API_1_AwardBadge(webapp2.RequestHandler):
  def post(self):
    start = time.time()
    api_key = self.request.get('apikey')
    account_id = self.request.get('accountid')
    user_id = self.request.get('userid')
    badge_ref_id = self.request.get('badgeid')
    reason = self.request.get('reason')

    clean = XssCleaner()
    reason = clean.strip(reason)
    logdiction = {'event':'awardbadge', 
                  'api':'award_badge',
                  'badgeid':badge_ref_id,
                  'is_api':'yes',
                  'ip':self.request.remote_addr,
                  'user':user_id,
                  'account':account_id,
                  'success':'true'}

    # Get the account 
    acc = accounts_dao.authorize_api(account_id, api_key)
    if not acc:
      logdiction['success'] = 'false'
      logdiction['details'] = auth_error()
      logs.create(logdiction)
      self.response.out.write(auth_error())
      return 

    if not user_id or not badge_ref_id:
      logdiction['success'] = 'false'
      logdiction['details'] = bad_args()
      logs.create(logdiction)
      self.response.out.write(bad_args())
      error("User id or badge id was not given")
      return  

    # Make sure we have a legit badge before getting/creating a user
    badge_key = badges_dao.get_key_from_badge_id(account_id, badge_ref_id)
    if not badge_key:
      logdiction['success'] = 'false'
      logdiction['details'] = badge_error()
      logs.create(logdiction)
      self.response.out.write(badge_error())
      return  
  
    # Get the user
    user_ref = users_dao.get_or_create_user(account_id, user_id, acc)
    if not user_ref:
      logdiction['success'] = 'false'
      logdiction['details'] = db_error()
      logs.create(logdiction)
      self.response.out.write(db_error())
      return 
 
    badge_instance_key = badges_dao.get_badge_instance_key(badge_key, user_id) 
    # If the user already has it, skip the award
    badge_ref = badges_dao.get_badge_instance(badge_instance_key)
    if badge_ref:
      if badge_ref.awarded == "yes":
        logs.create(logdiction)
        self.response.out.write(success_ret())
        timing(start)
        return  

    # Get the Badge Type (used as a reference for the instances) 
    badge_ref = badges_dao.get_badge(badge_key)
    if not badge_ref:
      self.response.out.write(badge_error())
      return  

    if not reason:
      reason = badge_ref.description

    link = badge_ref.downloadLink
    new_badge_instance = badges_dao.create_badge_instance(
                                    badge_instance_key,
                                    badge_ref,
                                    user_ref,
                                    "yes", #isawarded
                                    0, #points
                                    0, #points_needed
                                    "private",
                                    link,
                                    reason)
    name = badges_dao.get_badge_name_from_instance_key(badge_instance_key)
    notifier.user_badge_award(user_ref, "Badge Awarded", link, reason, acc, badge_ref_id)
    logs.create(logdiction)
    self.response.out.write(success_ret())
    timing(start)
    return  

  def get(self):
    self.redirect('/html/404.html')

class API_1_RemoveBadge(webapp2.RequestHandler):
  def post(self):
    start = time.time()
    api_key = self.request.get('apikey')
    account_id = self.request.get('accountid')
    user_id = self.request.get('userid')
    badge_ref_id = self.request.get('badgeid')
    logdiction = {'event':'removebadge', 
                  'api':'remove_badge',
                  'badgeid':badge_ref_id,
                  'is_api':'yes',
                  'ip':self.request.remote_addr,
                  'user':user_id,
                  'account':account_id,
                  'success':'true'}

    # Get the account 
    acc = accounts_dao.authorize_api(account_id, api_key)
    if not acc:
      logdiction['success'] = 'false'
      logdiction['details'] = auth_error()
      logs.create(logdiction)
      self.response.out.write(auth_error())
      return 

    if not user_id or not badge_ref_id:
      logdiction['success'] = 'false'
      logdiction['details'] = bad_args()
      logs.create(logdiction)
      self.response.out.write(bad_args())
      return  

    badge_key = badges_dao.get_key_from_badge_id(account_id, badge_ref_id)
    if not badge_key:
      logdiction['success'] = 'false'
      logdiction['details'] = badge_error()
      logs.create(logdiction)
      self.response.out.write(badge_error())
      return  
  
    # Get the user
    user_ref = users_dao.get_or_create_user(account_id, user_id, acc)
    if not user_ref:
      logdiction['success'] = 'false'
      logdiction['details'] = db_error()
      logs.create(logdiction)
      self.response.out.write(db_error())
      return 
 
    badge_instance_key = badges_dao.get_badge_instance_key(badge_key, user_id) 
    # Get the Badge Type (used as a reference for the instances) 
    badge_ref = badges_dao.get_badge(badge_key)
    if not badge_ref:
      logdiction['success'] = 'false'
      logdiction['details'] = badge_error()
      logs.create(logdiction)
      self.response.out.write(badge_error())
      return  

    try:
      new_badge_instance = badges_dao.delete_badge_instance(badge_instance_key)
    except:
      logdiction['success'] = 'false'
      logdiction['details'] = db_error()
      logs.create(logdiction)
      self.response.out.write(db_error())
      return 
    logs.create(logdiction)
    self.response.out.write(success_ret())
    timing(start)
    return  

  def get(self):
    self.redirect('/html/404.html')


class API_1_GetWidget(webapp2.RequestHandler):
  def post(self):
    """This post is for priming/prefetching, 
       not actually delivering the widget
    """
    start = time.time()
    api_key = self.request.get('apikey')
    account_id = self.request.get('accountid')
    user_id = self.request.get('userid')
    widget_type = self.request.get('widget')
    logdiction = {'event':'prefetchwidget', 
                  'api':'get_widget',
                  'user':user_id,
                  'is_api':'yes',
                  'ip':self.request.remote_addr,
                  'account':account_id,
                  'widget':widget_type,
                  'success':'true'}

    if widget_type not in constants.VALID_WIDGETS:
      logdiction['success'] = 'false'
      logdiction['details'] = "Using an invalid widget name"
      logs.create(logdiction)
      self.response.out.write(bad_args())
      return
 
    # Get the account 
    acc_ref = accounts_dao.authorize_api(account_id, api_key)
    if not acc_ref:
      logdiction['success'] = 'false'
      logdiction['details'] = auth_error()
      logs.create(logdiction)
      self.response.out.write(auth_error())
      return 

    if not user_id and widget_type in constants.WIDGETS_THAT_DONT_NEED_A_USER:
      user_id = constants.ANONYMOUS_USER

    if not user_id:
      logdiction['success'] = 'false'
      logdiction['details'] = bad_args()
      logs.create(logdiction)
      self.response.out.write(bad_args())
      return  

    user_ref = None
    if user_id: 
      user_ref = users_dao.get_user_with_key(user_id)

    if not user_ref and user_id == constants.ANONYMOUS_USER:
      users_dao.create_new_user(account_id, constants.ANONYMOUS_USER) 

    #acc_ref = users_dao.get_account_from_user(user_ref)
    # TODO Need to measure if there is an actual gain from this prefetching
    # or if it's causing unnecessary contention
    values = getattr(self, widget_type + "_values")(user_ref, acc_ref, 500, 300)
    logs.create(logdiction)
    return  
 
  
  def get(self):
    """ Users fetch their widgets from here """
    start = time.time()
    user_key = self.request.get('u')

    if not user_key:
      self.redirect('/html/404.html') 
      return 

    height = self.request.get('height')
    width = self.request.get('width')
    widget_type = self.request.get('widget')
    if widget_type not in constants.VALID_WIDGETS:
      self.redirect('/html/404.html')
      error("Fetching widget type " + str(widget_type))
      return
    
    # TODO make sure the account has permission to the type of widget
    # as of right now all widgets are enabled
    user_ref = users_dao.get_user_with_key(user_key)
    acc_ref = users_dao.get_account_from_user(user_ref)
    user_id = ""
    acc_id = ""
    if user_ref: user_id = user_ref.key().name()
    if acc_ref: acc_id = acc_ref.key().name()

    logdiction = {'event':'viewwidget', 
                  'api':'get_widget',
                  'user':user_id,
                  'is_api':'yes',
                  'ip':self.request.remote_addr,
                  'account':acc_id,
                  'widget':widget_type,
                  'success':'true'}

    values = getattr(self, widget_type + "_values")(user_ref, acc_ref, height, width)
    path = os.path.join(os.path.dirname(__file__), 'widgets/v1.0/' +
           widget_type + ".html")
    #TODO minify temp code, lots of white space right now
    temp = template.render(path, values)   

    logs.create(logdiction)
    self.response.out.write(temp)
    timing(start)
    return  

  def trophy_case_values(self, user_ref, acc_ref, height, width):
    badges = badges_dao.get_user_badges(user_ref)
    tcase_ref = None
    if not acc_ref:
      tcase_ref = TrophyCase()
    else:
      try:
        tcase_ref = acc_ref.trophyWidget
      except:
        tcase_ref = widgets_dao.add_trophy_case(acc_ref)

    awarded_badges= []
    for b in badges:
      if b.awarded == "yes":
        awarded_badges.append(b)
    # here we get the custom trophy case settings
    # Grab all the badge urls
    ret = {"status":"success"}
     
    for ii in tcase_ref.properties():
      ret[ii] = getattr(tcase_ref, ii)
    ret["badges"] = awarded_badges

    # Internal div's need to be slighy smaller than the iframe
    if width and height:
      try:
        width = int(width)
        height = int(height)
        # How did I get this equation? Trial and error.
        height = height - 2 *int(ret['borderThickness']) - 8
        width = width - 2 *int(ret['borderThickness']) - 8
        ret['height'] = height
        ret['width'] = width
      except:
        pass
    return ret 

  def notifier_values(self, user_ref, acc_ref, height, width):
    token = 0
    notifier_ref = None
    if not acc_ref:
      notifier_ref = Notifier()
    else:
      try:
        notifier_ref = acc_ref.notifierWidget
      except:
        notifier_ref = widgets_dao.add_notifier(acc_ref)

    token = notifier.get_channel_token(user_ref)

    ret = {"status":"success"}
    ret["token"] = token
    # here we get the custom settings
    for ii in notifier_ref.properties():
      ret[ii] = getattr(notifier_ref, ii)

    # Internal div's need to be slighy smaller than the iframe
    if width and height:
      try:
        width = int(width)
        height = int(height)
        # How did I get this equation? Trial and error.
        height = height - 2 *int(ret['borderThickness']) - 8
        width = width - 2 *int(ret['borderThickness']) - 16
        #height = height - 2 *int(ret['borderThickness']) - 8
        #width = width - 2 *int(ret['borderThickness']) - 8 
        ret['height'] = height
        ret['width'] = width
      except:
        pass
     
    return ret

  def milestones_values(self, user_ref, acc_ref, height, width):
    user_badges = badges_dao.get_user_badges(user_ref)
    acc_badges = badges_dao.get_rendereable_badgeset(acc_ref)
    mcase_ref = None
    if not acc_ref:
      mcase_ref = Milestones()
    else:
      try:
        mcase_ref = acc_ref.milestoneWidget
      except:
        mcase_ref = widgets_dao.add_milestones(acc_ref)

    if user_ref and user_ref.userid == constants.ANONYMOUS_USER:
      user_badges = []

    badge_count = 0
    display_badges = []
    for badge in user_badges:
      b = {}
      try:
        # In case the badge was removed, we'll skip it
        b["badgeRef"] = badge.badgeRef
      except Exception, e:
        continue
      if badge.awarded == "yes":
        b["awarded"] = True
      else:
        b["awarded"] = True
      b["id"] = badge_count 
      b["awarded"] = badge.awarded
      b["pointsRequired"] = badge.pointsRequired

      # backward compatibility
      if badge.pointsRequired == 9999999999:
        b["pointsRequired"] = 0
   
      if badge.pointsEarned > badge.pointsRequired:
        b["pointsEarned"] = badge.pointsRequired
      else:  
        b["pointsEarned"] = badge.pointsEarned
      b["resource"] = badge.resource
      b["reason"] = badge.reason
      b["downloadLink"] = badge.downloadLink
      b["id"] = badge_count
      badge_count += 1
      display_badges.append(b)
    # Put all badges that have not been awarded
    to_add = []
    for aa in acc_badges:
      is_there = False
      for dd in display_badges:
        if aa["key"] == dd["badgeRef"].key().name():
          is_there = True
      if not is_there:
        b = {}
        b["id"] = badge_count 
        b["awarded"] = False
        b["pointsEarned"] = 0
        b["pointsRequired"] = 0
        # This name should not have changed
        b["resource"] = ""
        b["reason"] = aa["description"]
        b["downloadLink"] = aa["downloadLink"]
        badge_count += 1
        to_add.append(b)
    display_badges.extend(to_add)
    ret = {"status":"success"}
     
    for ii in mcase_ref.properties():
      ret[ii] = getattr(mcase_ref, ii)
    ret["badges"] = display_badges

    # Internal div's need to be slighy smaller than the iframe
    if width and height:
      try:
        width = int(width)
        height = int(height)
        # How did I get this equation? Trial and error.
        height = height - 2 *int(ret['borderThickness']) - 8
        width = width - 2 *int(ret['borderThickness']) - 8
        ret['height'] = height
        ret['width'] = width
      except:
        pass
    ret['barSize'] = ret['imageSize']
    return ret 

  def leaderboard_values(self, user_ref, acc_ref, height, width):
    leader_ref = None
    if not acc_ref:
      leader_ref = Leaderboard()
    else: 
      try:
        leader_ref = acc_ref.leaderWidget
        if leader_ref == None:
          leader_ref = widgets_dao.add_leader(acc_ref)
      except:
        leader_ref = widgets_dao.add_leader(acc_ref)

    # here we get the custom rank settings
    ret = {"status":"success"}
    ret['users'] = get_top_users(acc_ref) 
    
    for ii in leader_ref.properties():
      ret[ii] = getattr(leader_ref, ii)

    # Internal div's need to be slighy smaller than the iframe
    if width and height:
      try:
        width = int(width)
        height = int(height)
        # How did I get this equation? Trial and error.
        height = height - 2 *int(ret['borderThickness']) - 8
        width = width - 2 *int(ret['borderThickness']) - 8
        ret['height'] = height
        ret['width'] = width
      except:
        pass
    
    return ret

  def points_values(self, user_ref, acc_ref, height, width):
    points = 0
    if user_ref:
      points = user_ref.points
    points_ref = None
    if not acc_ref:
      points_ref = Points()
    else:
      try:
        points_ref = acc_ref.pointsWidget
      except:
        points_ref = widgets_dao.add_points(acc_ref)
    ret = {"status":"success"}
     
    # here we get the custom points settings
    for ii in points_ref.properties():
      ret[ii] = getattr(points_ref, ii)
    points = format_integer(points) 
    ret['points'] = points
   
    # Internal div's need to be slighy smaller than the iframe
    if width and height:
      try:
        width = int(width)
        height = int(height)
        # How did I get this equation? Trial and error.
        height = height - 2 *int(ret['borderThickness']) - 8
        width = width - 2 *int(ret['borderThickness']) - 8
        ret['height'] = height
        ret['width'] = width
      except:
        pass
    return ret

  def rank_values(self, user_ref, acc_ref, height, width):
    rank = 0
    if user_ref:
      rank = user_ref.rank
    rank_ref = None
    if not acc_ref:
      rank_ref = Rank()
    else: 
      try:
        rank_ref = acc_ref.rankWidget
      except:
        rank_ref = widgets_dao.add_rank(acc_ref)

    # here we get the custom rank settings
    ret = {"status":"success"}
     
    for ii in rank_ref.properties():
      ret[ii] = getattr(rank_ref, ii)
    rank = calculate_rank(user_ref, acc_ref)
    if rank == constants.NOT_RANKED:
      ret['rank'] = "Unranked"
    else:
      ret['rank']= "&#35 " + format_integer(rank)
    # Internal div's need to be slighy smaller than the iframe
    if width and height:
      try:
        width = int(width)
        height = int(height)
        # How did I get this equation? Trial and error.
        height = height - 2 *int(ret['borderThickness']) - 8
        width = width - 2 *int(ret['borderThickness']) - 8
        ret['height'] = height
        ret['width'] = width
      except:
        pass
    
    return ret

class API_1_AwardPoints(webapp2.RequestHandler):
  def post(self):
    start = time.time()
    api_key = self.request.get('apikey')
    account_id = self.request.get('accountid')
    user_id = self.request.get('userid')
    newpoints = self.request.get('pointsawarded')
    reason = self.request.get('reason')
    logdiction = {'event':'awardpoints', 
                  'api':'award_points',
                  'points':newpoints,
                  'is_api':'yes',
                  'ip':self.request.remote_addr,
                  'user':user_id,
                  'account':account_id,
                  'success':'true'}

    clean = XssCleaner()
    if reason:
      reason = clean.strip(reason)
    else:
      reason = ""

    # Get the account 
    acc = accounts_dao.authorize_api(account_id, api_key)
    if not acc:
      logdiction['success'] = 'false'
      logdiction['details'] = auth_error()
      logs.create(logdiction)
      self.response.out.write(auth_error())
      return 

    try:
      newpoints = int(newpoints)
    except:
      logdiction['success'] = 'false'
      logdiction['details'] = "Points given was not a number"
      logs.create(logdiction)
      self.response.out.write(bad_args())
      error("Points given was not an integer")
      return  

    # Create the user if it doesnt exist
    user_ref = users_dao.get_or_create_user(account_id, user_id, acc)
    if not user_ref:
      logdiction['success'] = 'false'
      logdiction['details'] = db_error()
      logs.create(logdiction)
      self.response.out.write(db_error())
      return 

    incrArgs = {"points":newpoints}
    user_key = users_dao.get_user_key(account_id, user_id)
    dbret = users_dao.update_user(user_key, None, incrArgs)
    if not dbret:
      logdiction['success'] = 'false'
      logdiction['details'] = db_error()
      logs.create(logdiction)
      self.response.out.write(db_error())
      error("Unable to update points field account %s, user %s, key: %s"%\
            (account_id,user_id, user_key))
      return  
    if not reason:
      try:
        reason = acc.notifierWidget.title
      except:
        reason = "Points Awarded"
    notifier.user_points(user_ref, newpoints, reason, acc)
      
    logs.create(logdiction)
    self.response.out.write(success_ret())
    timing(start)
    return
   
  def get(self):
    self.redirect('/html/404.html')
    return 

class API_1_TestCleanup(webapp2.RequestHandler):
  def post(self):
    isLocal = os.environ['SERVER_SOFTWARE'].startswith('Dev')
    if not isLocal:
      return
    api_key = self.request.get('apikey')
    account_id = self.request.get('accountid')
    badge_id = self.request.get('badgeid')
    badge_theme = self.request.get('theme')
    user_id = self.request.get('user')
    if not badge_theme or not badge_id or not account_id or not api_key:
      ret = bad_args()
      self.response.out.write(ret)
      return

    user_key = users_dao.get_user_key(account_id, user_id)
    user_ref = users_dao.get_user(account_id, user_id)
    if user_ref:
      badge_instances = badges_dao.get_user_badges(user_ref)
      for b in badge_instances:
        badges_dao.delete_badge_instance(b.key().name())
      users_dao.delete_user(user_key)

    trophy_case_widget = TrophyCase(key_name=account_id)
    points_widget = Points(key_name=account_id)
    rank_widget = Rank(key_name=account_id)
    notifier_widget = Notifier(key_name=account_id)
    leader_widget = Leaderboard(key_name=account_id)
    milestones_widget = Milestones(key_name=account_id)
    acc = Accounts(key_name=account_id,
                   email=account_id,
                   password="xxxxxxxxx",
                   isEnabled=constants.ACCOUNT_STATUS.ENABLED, 
                   accountType="admin",
                   paymentType="free",
                   cookieKey="xxxxxxxxx", 
                   apiKey=api_key, 
                   trophyWidget=trophy_case_widget,
                   pointsWidget=points_widget,
                   rankWidget=rank_widget,
                   leaderWidget=leader_widget,
                   milestoneWidget=milestones_widget)

     # delete ten badges
    for ii in range(0,10):
      badgeKey = badges_dao.create_badge_key(account_id, badge_theme, str(ii), "private")
      badges_dao.delete_badge_image(badgeKey)
      badges_dao.delete_badge(badgeKey)

    widgets_dao.delete_widget(account_id, "TrophyCase")
    widgets_dao.delete_widget(account_id, "Points")
    widgets_dao.delete_widget(account_id, "Rank")
    widgets_dao.delete_widget(account_id, "Leaderboard")
    widgets_dao.delete_widget(account_id, "Notifier")
    widgets_dao.delete_widget(account_id, "Milestones")
    accounts_dao.delete_account(account_id)
    self.response.out.write(success_ret())
    return

  def  get(self):
    self.redirect('/html/404.html')
    return  

# Secret only valid for local testing
TOPSECRET = "8u8u9i9i"
class API_1_Test(webapp2.RequestHandler):
  def post(self):
    isLocal = os.environ['SERVER_SOFTWARE'].startswith('Dev')
    if not isLocal:
      return
    secret = self.request.get('secret')
    if secret != TOPSECRET:
      bad_args()  
      return
    api_key = self.request.get('apikey')
    account_id = self.request.get('accountid')
    badge_id = self.request.get('badgeid')
    badge_theme = self.request.get('theme')
    if not badge_theme or not badge_id or not account_id or not api_key:
      ret = bad_args()
      self.response.out.write(ret)
      return
    acc = accounts_dao.create_account(account_id, "xxx000xxx", enable=True)

    from serverside.entities import memcache_db
    acc.apiKey = "ABCDEFGHI"
    memcache_db.save_entity(acc, account_id)
    # remote paths are used because the SDK cannot fetch from itself 
    # because it is single threaded and would cause deadlock
    badge_list = ["http://cdn2.iconfinder.com/data/icons/crystalproject/128x128/apps/keditbookmarks.png",
                  "http://cdn4.iconfinder.com/data/icons/Merry_Christmas_by_jj_maxer/golden%20star.png",
                  "http://cdn1.iconfinder.com/data/icons/CrystalClear/128x128/actions/bookmark.png",
                  "http://cdn4.iconfinder.com/data/icons/token/Token,%20128x128,%20PNG/Star-Favorites.png",
                  "http://cdn4.iconfinder.com/data/icons/supermario/PNG/Star.png",
                  "http://cdn5.iconfinder.com/data/icons/SOPHISTIQUE/graphics/png/128/star.png",
                  "http://cdn3.iconfinder.com/data/icons/humano2/128x128/actions/bookmark-new.png",
                  "http://cdn2.iconfinder.com/data/icons/web2/Icons/Favorite_128x128.png",
                  "http://cdn5.iconfinder.com/data/icons/water_gaming_pack/128/star_wars_battlefront.png",
                  "http://cdn2.iconfinder.com/data/icons/spaceinvaders/blackhole.png"]
    # Create ten badges
    for ii in range(0,10):
      newbadge = badge_list[ii]

      try:
        result = urlfetch.fetch(url=newbadge)
      except:
        error("Is one of the badges no longer available? Check %s"%newbadge)
        return
 
      imgbuf = result.content
      if  len(imgbuf) == 0:
        error("One of the downloads did not work! url:%s"%newbadge)
        return
      badge_key = badges_dao.create_badge_key(account_id, badge_theme, str(ii), "private")
      # Create the file
      file_name = files.blobstore.create(mime_type='application/octet-stream')

      # Open the file and write to it
      with files.open(file_name, 'a') as f:
        f.write(imgbuf)

      # Finalize the file. Do this before attempting to read it.
      files.finalize(file_name)

      # Get the file's blob key
      blob_key = files.blobstore.get_blob_key(file_name)
      blob_info = blobstore.BlobInfo.get(blob_key)

      # TODO test with different types of images
      badges_dao.create_badge_type(badge_key,
                      str(ii),
                      "badge description",
                      acc,
                      badge_theme,
                      "png",
                      blob_info=blob_info)
      # End of for loop
    self.response.out.write(success_ret())
    return        
  def get(self):
    self.redirect('/html/404.html')
    return  

# Hidden menu APIs, badges should be created via console
class API_1_CreateBadge(webapp2.RequestHandler):
  def post(self):
    start = time.time()
    api_key = self.request.get('apikey')
    account_id = self.request.get('accountid')
    badge_name = self.request.get('name')
    theme = self.request.get('theme')
    description = self.request.get('description')
    imagelink = self.request.get('imagelink')
    acc = accounts_dao.authorize_api(account_id, api_key)
    logdiction = {'event':'createbadge', 
                  'ip':self.request.remote_addr,
                  'is_api':'yes',
                  'api':'createbadge',
                  'account':account_id,
                  'success':'true'}

    if not acc:
      logdiction['success'] = 'false'
      logdiction['details'] = auth_error()
      logs.create(logdiction)
      self.response.out.write(auth_error())
      return 

    if not imagelink or not badge_name or not theme or not description:
      logdiction['success'] = 'false'
      logdiction['details'] = bad_args()
      logs.create(logdiction)
      self.response.out.write(bad_args())
      return 
      
    badge_key = badges_dao.create_badge_key(account_id, theme, badge_name, "private")
    logdiction['details'] = badge_key + " " + imagelink
    result = ""
    try:
      result = urlfetch.fetch(url=imagelink)
    except:
      error("Unable to download badge")
      self.response.out.write(bad_args())
      return

    imgbuf = result.content
    if  len(imgbuf) == 0:
      error("One of the downloads did not work! url:%s"%imagelink)
      self.response.out.write(bad_args())
      return
    def get_file_ext(filename):
      ii = filename.rfind(".")
      if ii == -1:
        return "png"
      else:
        return filename[ii + 1:]

    file_name = files.blobstore.create(mime_type='image/'+ get_file_ext(imagelink))

    with files.open(file_name, 'a') as f:
      f.write(imgbuf)

    files.finalize(file_name)

    blob_key = files.blobstore.get_blob_key(file_name)
    blob_info = blobstore.BlobInfo.get(blob_key)
    badges_dao.create_badge_type(badge_key,
                    badge_name,
                    description,
                    acc,
                    theme,
                    get_file_ext(imagelink),
                    blob_info=blob_info)
    self.response.out.write(success_ret())
    return        
 

app = webapp2.WSGIApplication([
  ('/api/1/', API_1_Status),
  ('/api/1/updateuser', API_1_UpdateUser),
  ('/api/1/getuserdata', API_1_GetUserData),
  ('/api/1/awardbadge', API_1_AwardBadge),
  ('/api/1/removebadge', API_1_RemoveBadge),
  ('/api/1/awardbadgepoints', API_1_AwardBadgePoints),
  ('/api/1/awardpoints', API_1_AwardPoints),
  ('/api/1/test', API_1_Test),
  ('/api/1/testcleanup', API_1_TestCleanup),
  ('/api/1/getwidget', API_1_GetWidget),
  # Secret menu APIs 
  ('/api/1/createbadge', API_1_CreateBadge)
], debug=False)

"""
def main():
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
  main()
"""
