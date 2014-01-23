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
from serverside.dao import accounts_dao
from serverside.dao import badges_dao
from entities.accounts import Accounts
from entities.badges import *
from entities.users import *
from entities.logs import *
from entities.counter import *
from google.appengine.ext import db
import webapp2
from serverside import constants
from serverside.session import Session
from tools.utils import account_login_required
from tools.xss import XssCleaner, XssCleaner
from serverside.fantasm.action import FSMAction, DatastoreContinuationFSMAction
from serverside.fantasm import fsm
import cgi
import logging
import os
import wsgiref.handlers
import string
import datetime
import json

def stripMilSecs(d):
  return datetime.datetime(d.year, d.month, d.day, d.hour, d.minute, d.second)

def stripHours(d):
  return datetime.datetime(d.year, d.month, d.day)

class RunAnalytics(webapp2.RequestHandler):
  def get(self):
    now = datetime.datetime.now()
    a_day_ago = now - datetime.timedelta(days=1)

    context = {}
    context['start_time'] = str(stripMilSecs(a_day_ago))
    context['end_time'] = str(stripMilSecs(now))
    fsm.startStateMachine('CountAwardedBadges', [context])
    fsm.startStateMachine('CountAwardedPoints', [context])
    fsm.startStateMachine('CountAwardedBadgePoints', [context])
    fsm.startStateMachine('CountAPICalls', [context])

VALID_ANALYTICS = ["badges", "badgepoints", "points", "apicalls"]

class GetAnalytics(webapp2.RequestHandler):
  @account_login_required
  def get(self):
    current_session = Session().get_current_session(self)
    acc = current_session.get_account_entity()
    a_type = self.request.get("type")
    if a_type not in VALID_ANALYTICS:
      return json.dumps({'success':'false'})

    values = getattr(self, a_type + "_values")(acc)
    self.response.out.write(json.dumps(values))


  @account_login_required
  def post(self):
    current_session = Session().get_current_session(self)
    acc = current_session.get_account_entity()
    a_type = self.request.get("type")
    if a_type not in VALID_ANALYTICS:
      return json.dumps({'success':'false'})

    values = getattr(self, a_type + "_values")(acc)
    self.response.out.write(json.dumps(values))

  def badges_values(self, acc):
    q = BadgeBatch.all().filter("account_key =", acc.key().name())
    values = {"success": "true"}
    res = q.fetch(1000) 
    values['total'] = q.count() or 1
    values['entry'] = []
    values['badges'] = []
    values['numbadges'] = 0
    badges = set()
    for ii in res:
      ent = {'date':ii.date.strftime("%Y-%m-%d"),
             'count':str(ii.counter),
             'badgeid':ii.badgeid}
      values['entry'].append(ent)
      badges.add(ii.badgeid)
    else:
      ent = {'date':datetime.datetime.now().strftime("%Y-%m-%d"),
             'count':"0",
             'badgeid':"none"}
      values['entry'].append(ent)
      badges.add("none")
             
    badges = list(badges)
    #badges = badges_dao.get_all_badges_for_account(acc)
    for ii in badges:
      values['badges'].append(ii)
      values['numbadges'] += 1
    return values

  def badgepoints_values(self, acc):
    q = BadgePointsBatch.all().filter("account_key =", acc.key().name())
    values = {"success": "true"}
    res = q.fetch(1000) 
    values['total'] = q.count() or 1
    values['entry'] = []
    values['badges'] = []
    values['numbadges'] = 0
    badges = set()
    for ii in res:
      ent = {'date':ii.date.strftime("%Y-%m-%d"),
             'count':str(ii.counter),
             'badgeid':ii.badgeid}
      values['entry'].append(ent)
      badges.add(ii.badgeid) 
    else:
      ent = {'date':datetime.datetime.now().strftime("%Y-%m-%d"),
             'count':"0",
             'badgeid':"none"}
      values['entry'].append(ent)
      badges.add("none")
 
    # = badges_dao.get_all_badges_for_account(acc)
    badges = list(badges)
    for ii in badges:
      values['badges'].append(ii)
      values['numbadges'] += 1
    return values

  def points_values(self, acc):
    q = PointBatch.all().filter("account_key =", acc.key().name())
    values = {"success": "true"}
    res = q.fetch(1000) 
    values['total'] = q.count() or 1
    values['entry'] = []
    for ii in res:
      ent = {'date':ii.date.strftime("%Y-%m-%d"),
             'count':str(ii.counter)}
      values['entry'].append(ent)
    else:
      ent = {'date':datetime.datetime.now().strftime("%Y-%m-%d"),
             'count':"0"}
      values['entry'].append(ent)
    return values

  def apicalls_values(self, acc):
    q = APICountBatch.all().filter("account_key =", acc.key().name())
    values = {"success": "true"}
    res = q.fetch(1000) 
    values['total'] = q.count() or 1
    values['entry'] = []
    for ii in res:
      ent = {'date':ii.date.strftime("%Y-%m-%d"),
             'count':str(ii.counter)}
      values['entry'].append(ent)
    else:
      ent = {'date':datetime.datetime.now().strftime("%Y-%m-%d"),
             'count':"0"}
      values['entry'].append(ent)
    return values


###############################################
# Start of State Machine 
# CountAwardedBadges
###############################################
"""
Badge Award Counting State Machine
This class starts a task for each account 
"""
class AllAccountsClass(DatastoreContinuationFSMAction):
  def getQuery(self, context, obj):
    return Accounts.all()

  def execute(self, context, obj):
    if not obj['result']:
      return None
    acc = obj['result']
    if acc: 
      context['account_key'] = acc.key().name()
      return "peraccount"

"""
Second state for each account's badges to count over
"""
class PerAccountClass(DatastoreContinuationFSMAction):
  def getQuery(self, context, obj):
    account_key = context['account_key']
    account_ref = accounts_dao.get(account_key)
    return Badges.all().filter('creator =', account_ref)
 
  def execute(self, context, obj):
    if not obj['result']:
      return None
    ii = obj['result']
    context['badgeid'] = ii.theme + '-' + ii.name + '-' + ii.permissions
    return "perbadge" 

"""
Awarded Badge Counting State Machine
"""
class PerBadgeClass(DatastoreContinuationFSMAction):
  def getQuery(self, context, obj):
    start_time = datetime.datetime.strptime(context['start_time'], "%Y-%m-%d %H:%M:%S")
    end_time = datetime.datetime.strptime(context['end_time'], "%Y-%m-%d %H:%M:%S")
    return Logs.all().filter("account =", context['account_key']).filter("badgeid =", context['badgeid']).filter("event =", "notify_badge").filter("date >", start_time).filter("date <", end_time)


  def execute(self, context, obj):
    # Create a counter initialized the count to 0
    # This way we'll at least know when its a sum of 0
    # rather than having nothing to signify that it ran
    def tx():
      batch_key = context['account_key'] + '-' + \
                  context['badgeid'] + '-' + \
                  context['end_time']

      batch = BadgeBatch.get_by_key_name(batch_key)
      if not batch:
        end_time = datetime.datetime.strptime(context['end_time'], "%Y-%m-%d %H:%M:%S")
        batch = BadgeBatch(key_name=batch_key,
                       badgeid=context['badgeid'],
                       account_key=context['account_key'],
                       date=end_time)
        batch.put()
    if not obj['result']:
      return None
    db.run_in_transaction(tx) 
    return "count"
   
"""
This class spawns a task for each log.
"""
class CountAwardedBadgesClass(FSMAction):
  def execute(self, context, obj):
    """Transactionally update our batch counter"""
    batch_key = context['account_key'] + '-' + \
                context['badgeid'] + '-' + \
                context['end_time']

    def tx():
      batch = BadgeBatch.get_by_key_name(batch_key)
      if not batch:
        # For whatever reason it was not already created in previous state
        end_time = datetime.datetime.strptime(context['end_time'], "%Y-%m-%d %H:%M:%S")
        batch = BadgeBatch(key_name=batch_key,
                       badgeid=context['badgeid'],
                       account_key=context['account_key'],
                       date=end_time)
        batch.put()
      batch.counter += 1
      batch.put()
    db.run_in_transaction(tx)

###############################################
# End of State Machine 
# CountAwardedBadges
###############################################
###############################################
###############################################
# Start of State Machine 
# CountAPICallsInitState
###############################################
"""
API Call Counting State Machine
This class starts a task for each account 
"""
class APICallsAllAccountsClass(DatastoreContinuationFSMAction):
  def getQuery(self, context, obj):
    return Accounts.all()

  def execute(self, context, obj):
    if not obj['result']:
      return None
    acc = obj['result']
    if acc: 
      context['account_key'] = acc.key().name()
      return "apicallsperaccount"

"""
Second state for each account's api calls for counting
"""
class APICallsPerAccountClass(DatastoreContinuationFSMAction):
  def getQuery(self, context, obj):
    start_time = datetime.datetime.strptime(context['start_time'], 
                                            "%Y-%m-%d %H:%M:%S")
    end_time = datetime.datetime.strptime(context['end_time'], 
                                            "%Y-%m-%d %H:%M:%S")
    return Logs.all().filter("account =", context['account_key']).filter("is_api =", "yes").filter("date >", start_time).filter("date <", end_time)

  def execute(self, context, obj):
    if not obj['result']:
      return None
    batch_key = context['account_key'] + '-' + \
                context['end_time']
    def tx():
      batch = APICountBatch.get_by_key_name(batch_key)
      if not batch:
        # Initialize counter
        end_time = datetime.datetime.strptime(context['end_time'], "%Y-%m-%d %H:%M:%S")
        batch = APICountBatch(key_name=batch_key,
                       account_key=context['account_key'],
                       date=end_time)
        batch.put()
 
    db.run_in_transaction(tx)
    return "count"
   
"""
This class fans in multiple logs
There may be failures in the computation
but its meant only for a rough estimate
"""
class CountAPICallsClass(FSMAction):
  def execute(self, contexts, obj):
    """Transactionally update our batch counter"""
    allcontext = {} 
    context_account = {}
    context_datetime = {}
    batch_key = None
    if len(contexts) < 1:
      return
    for index,ii in enumerate(contexts):
      batch_key = ii['account_key'] + '-' + \
                  ii['end_time']
      if batch_key in allcontext:
        allcontext[batch_key] += 1
      else:
        allcontext[batch_key] = 1
      context_account[batch_key] = ii['account_key']
      end_time = datetime.datetime.strptime(ii['end_time'], "%Y-%m-%d %H:%M:%S")
      context_datetime[batch_key] = end_time

    def tx(batch_key, count):
      batch = APICountBatch.get_by_key_name(batch_key)
      if not batch:
        batch = APICountBatch(key_name=batch_key,
                       account_key=context_account[batch_key],
                       date=context_datetime[batch_key])
        batch.put()
      batch.counter += count
      batch.put()

    # if a failure happens while in this loop, numbers will be inflated
    for ii in allcontext:
      db.run_in_transaction(tx, ii, allcontext[ii])
###############################################
# End of State Machine 
# CountAPICallsInitState
###############################################
###############################################
###############################################
# Start of State Machine 
# CountPointsInitState
###############################################
"""
Points Counting State Machine
This class starts a task for each account 
"""
class PointsAllAccountsClass(DatastoreContinuationFSMAction):
  def getQuery(self, context, obj):
    return Accounts.all()

  def execute(self, context, obj):
    if not obj['result']:
      return None
    acc = obj['result']
    if acc: 
      context['account_key'] = acc.key().name()
      return "pointsperaccount"

"""
Second state for each account's points awarded for counting
"""
class PointsPerAccountClass(DatastoreContinuationFSMAction):
  def getQuery(self, context, obj):
    start_time = datetime.datetime.strptime(context['start_time'], 
                                            "%Y-%m-%d %H:%M:%S")
    end_time = datetime.datetime.strptime(context['end_time'], 
                                            "%Y-%m-%d %H:%M:%S")
    return Logs.all().filter("account =", context['account_key']).filter("event =", "awardpoints").filter("date >", start_time).filter("date <", end_time).filter("success", "true")

  def execute(self, context, obj):
    if not obj['result']:
      return None
    batch_key = context['account_key'] + '-' + \
                context['end_time']
    end_time = datetime.datetime.strptime(context['end_time'], "%Y-%m-%d %H:%M:%S")

    context['points'] = obj['result'].points
    if not context['points']:
      context['points'] = 0

    def tx():
      batch = PointBatch.get_by_key_name(batch_key)
      if not batch:
        # Initialize counter
        batch = PointBatch(key_name=batch_key,
                       account_key=context['account_key'],
                       date=end_time)
        batch.put()
 
    db.run_in_transaction(tx)
    return "count"
   
"""
This class fans in multiple logs
If an error occurrs during this processing it is possible to have
inflated numbers.
"""
class CountPointsClass(FSMAction):
  def execute(self, contexts, obj):
    """Transactionally update our batch counter"""
    allcontext = {} 
    context_account = {}
    context_datetime = {}
    batch_key = None
    if len(contexts) < 1:
      return
    for index,ii in enumerate(contexts):
      batch_key = ii['account_key'] + '-' + \
                  ii['end_time']
      if batch_key in allcontext:
        allcontext[batch_key] += int(ii['points'])
      else:
        allcontext[batch_key] = int(ii['points'])
      context_account[batch_key] = ii['account_key']
      end_time = datetime.datetime.strptime(ii['end_time'], "%Y-%m-%d %H:%M:%S")
      context_datetime[batch_key] = end_time

    def tx(batch_key, count):
      batch = PointBatch.get_by_key_name(batch_key)
      if not batch:
        batch = PointBatch(key_name=batch_key,
                       account_key=context_account[batch_key],
                       date=context_datetime[batch_key])
        batch.put()
      batch.counter += int(count)
      batch.put()

    # if a failure happens while in this loop, numbers will be inflated
    for ii in allcontext:
      db.run_in_transaction(tx, ii, allcontext[ii])
###############################################
# End of State Machine 
# CountAPICallsInitState
###############################################
###############################################
# Start of State Machine 
# CountAwardedBadgePoints
###############################################
"""
Badge Point Award Counting State Machine
This class starts a task for each account 
"""
class BadgePointsAllAccountsClass(DatastoreContinuationFSMAction):
  def getQuery(self, context, obj):
    return Accounts.all()

  def execute(self, context, obj):
    if not obj['result']:
      return None
    acc = obj['result']
    if acc: 
      context['account_key'] = acc.key().name()
      return "peraccount"

"""
Second state for each account's badges to count over
"""
class BadgePointsPerAccountClass(DatastoreContinuationFSMAction):
  def getQuery(self, context, obj):
    account_key = context['account_key']
    account_ref = accounts_dao.get(account_key)
    return Badges.all().filter('creator =', account_ref)
 
  def execute(self, context, obj):
    if not obj['result']:
      return None
    ii = obj['result']
    context['badgeid'] = ii.theme + '-' + ii.name + '-' + ii.permissions
    return "perbadge" 

"""
Awarded Badge Counting State Machine
"""
class PerBadgePointsClass(DatastoreContinuationFSMAction):
  def getQuery(self, context, obj):
    start_time = datetime.datetime.strptime(context['start_time'], "%Y-%m-%d %H:%M:%S")
    end_time = datetime.datetime.strptime(context['end_time'], "%Y-%m-%d %H:%M:%S")
    return Logs.all().filter("account =", context['account_key']).filter("badgeid =", context['badgeid']).filter("api =", "award_badge_points").filter("date >", start_time).filter("date <", end_time)


  def execute(self, context, obj):
    # Create a counter initialized the count to 0
    # This way we'll at least know when its a sum of 0
    # rather than having nothing to signify that it ran
    end_time = datetime.datetime.strptime(context['end_time'], "%Y-%m-%d %H:%M:%S")
    def tx():
      batch_key = context['account_key'] + '-' + \
                  context['badgeid'] + '-' + \
                  context['end_time']

      batch = BadgePointsBatch.get_by_key_name(batch_key)
      if not batch:
        batch = BadgePointsBatch(key_name=batch_key,
                       badgeid=context['badgeid'],
                       account_key=context['account_key'],
                       date=end_time)
        batch.put()
    if not obj['result']:
      return None
    db.run_in_transaction(tx) 
    if obj['result'].success == "true":
      context['points'] = str(obj['result'].points)
      return "count"
    else:
      return None
   
"""
This class spawns a task for each log.
"""
class CountAwardedBadgePointsClass(FSMAction):
  def execute(self, context, obj):
    """Transactionally update our batch counter"""
    batch_key = context['account_key'] + '-' + \
                context['badgeid'] + '-' + \
                context['end_time']

    def tx():
      batch = BadgePointsBatch.get_by_key_name(batch_key)
      if not batch:
        end_time = datetime.datetime.strptime(context['end_time'], "%Y-%m-%d %H:%M:%S")
        batch = BadgePointsBatch(key_name=batch_key,
                       badgeid=context['badgeid'],
                       account_key=context['account_key'],
                       date=end_time)
        batch.put()
      batch.counter += int(context['points'])
      batch.put()
    db.run_in_transaction(tx)


