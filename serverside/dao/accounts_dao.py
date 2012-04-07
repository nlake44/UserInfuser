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
'''
Created on Feb 14, 2011

psuedo DAO methods

@author: shan
'''
from serverside.constants import ACCOUNT_STATUS
from serverside.entities import memcache_db
from serverside.entities.accounts import Accounts
from serverside.entities.widgets import TrophyCase, Points, Rank, Notifier, \
  Leaderboard, Milestones
from serverside import constants 
from serverside.tools import utils
from serverside.dao import users_dao
import hashlib
import logging
import uuid


def create_account(email, 
                   password, 
                   enable=False,
                   account_type="bronze",
                   payment_type="free"):
  """
  Creates an account with all the other needed dependencies properly initialized.
  """
  
  
  """
  Required:
  email = db.EmailProperty(required=True)
  password = db.StringProperty(required=True);
  isEnabled = db.StringProperty(required=True, choices=ACCOUNT_STATUS.RANGE_OF_VALUES)
  accountType = db.StringProperty(required=True, choices=set(ACCOUNT_TYPES)) 
  paymentType = db.StringProperty(required=True,choices=set(PAYMENT_TYPES))
  cookieKey = db.StringProperty(required=True)
  apiKey = db.StringProperty(required=True)
  trophyWidget = db.ReferenceProperty(required=True, reference_class=TrophyCase)
  pointsWidget = db.ReferenceProperty(required=True, reference_class=Points)
  rankWidget = db.ReferenceProperty(required=True, reference_class=Rank)
  """
  
  new_trophy_case = TrophyCase(key_name=email)
  memcache_db.save_entity(new_trophy_case, email)

  new_rank = Rank(key_name=email)
  memcache_db.save_entity(new_rank, email)

  new_points = Points(key_name=email)
  memcache_db.save_entity(new_points, email)

  new_notifier = Notifier(key_name=email)
  memcache_db.save_entity(new_notifier, email)
 
  new_leader = Leaderboard(key_name=email)
  memcache_db.save_entity(new_leader, email)
  
  new_milestones = Milestones(key_name=email)
  memcache_db.save_entity(new_milestones, email)
  
  """ Generate an API key """
  api_key = str(uuid.uuid4())
  
  """ Hash the password """
  hashed_password = hashlib.sha1(password).hexdigest()
  
  enable_account = ACCOUNT_STATUS.PENDING_CREATE
  if enable:
    enable_account = ACCOUNT_STATUS.ENABLED
  
  newacc = Accounts(key_name = email,
                      email = email,
                      password = hashed_password,
                      isEnabled = enable_account,
                      accountType = account_type,
                      paymentType = payment_type,
                      apiKey = api_key,
                      cookieKey = "xxxxxxxxxxxxxx",
                      trophyWidget = new_trophy_case,
                      pointsWidget = new_points,
                      rankWidget = new_rank,
                      notifierWidget = new_notifier,
                      leaderWidget = new_leader,
                      milestoneWidget = new_milestones)
  
  try:
    memcache_db.save_entity(newacc, email)
  except:
    logging.error("Failed to create account")
 
  users_dao.create_new_user(email, constants.ANONYMOUS_USER)
 
  return newacc


def authenticate_web_account(account_id, password):
  entity = memcache_db.get_entity(account_id, "Accounts")
  if entity != None and entity.password == hashlib.sha1(password).hexdigest() and entity.isEnabled == ACCOUNT_STATUS.ENABLED:
    return entity
  else:
    return None

def authenticate_web_account_hashed(account_id, hashedpassword):
  entity = memcache_db.get_entity(account_id, "Accounts")
  if entity != None and entity.password == hashedpassword and entity.isEnabled == ACCOUNT_STATUS.ENABLED:
    return entity
  else:
    return None   
  
def change_account_password(email, new_password):
  """ Change value in data store, also do hashing """
  values = {"password" : hashlib.sha1(new_password).hexdigest()}
  
  try:
    memcache_db.update_fields(email, "Accounts", values)
    return True
  except:
    logging.info("Password change failed.")
    return False
  
def reset_password(email):
  """
  Generates a random password for the account, and saves into account.
  Returns the new password.
  Returns None if account lookup/update fails
  """
  account_entity = memcache_db.get_entity(email, "Accounts")
  ret = None
  if account_entity:
    random_str = utils.generate_random_string(8)
    if change_account_password(email, random_str):
      ret = random_str
    else:
      logging.info("Unable to change password.")
  else:
    logging.info("Password cannot be reset, account was not located.")
      
  return ret

def authorize_api(account_id, api_key):
  """
  return the account on success, non on failure
  """
  acc = None
  try:
    acc = memcache_db.get_entity(account_id, "Accounts")
  except:
    logging.error("Error getting account with key %s"%account_id)
    return None
  if not acc:
    logging.error("Permission error with null  account")
    return None
  if acc.apiKey != api_key or acc.isEnabled != constants.ACCOUNT_STATUS.ENABLED:
    logging.error("Permission error with %s account with %s api key versus %s"\
                  %(account_id, api_key, acc.apiKey))
    return None
  return acc

def delete_account(acc_key):
  memcache_db.delete_entity_with_key(acc_key, "Leaderboard")
  memcache_db.delete_entity_with_key(acc_key, "TrophyCase")
  memcache_db.delete_entity_with_key(acc_key, "Points")
  memcache_db.delete_entity_with_key(acc_key, "Rank")
  return memcache_db.delete_entity_with_key(acc_key, "Accounts")

def save(acc_ref):
  memcache_db.save_entity(acc_ref, acc_ref.key().name())

def get_all_accounts():
  accounts = []
  aset = Accounts.all()
  for a in aset:
    accounts.append(get(a.email))
  return accounts
  

def get(acc_key):
  return memcache_db.get_entity(acc_key, "Accounts")
