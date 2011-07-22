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
Created on Feb 24, 2011

psuedo DAO methods

@author: shan
'''
from serverside.entities.users import Users
from serverside.entities.accounts import Accounts
from serverside.entities import memcache_db
from serverside import constants 
from serverside.dao import badges_dao
import logging
import hashlib 
class ORDER_BY:
  CREATION_DATE = 1
  POINTS = 2
  RANK = 3
  USER_ID = 4
  PROFILE_NAME = 5
  BADGE_COUNT = 6

def get_user(account_id, user_id):
  user_ref = None
  user_key = get_user_key(account_id, user_id)
  try:
    user_ref = memcache_db.get_entity(user_key, "Users")
  except:
    logging.error("Error getting key %s for user %s and account %s"%\
          (user_key, user_id, account_id))
    return None
  return user_ref 

def get_users_by_page_by_order(account, offset, limit, order_by, asc = "ASC"):
  """
  Retrieve chunks of users from users table by specifying offset
  """
  logging.info("Retrieving users for account: " + account.email + " and ordering by: " + order_by)
  users = Users.gql("WHERE accountRef = :1 ORDER BY " + order_by + " " + asc, account).fetch(limit, offset)
  
  return users

def get_users_by_page(account, offset, limit, order_by = "userid"):
  return get_users_by_page_by_order(account, offset, limit, order_by)


def create_new_user(account_id, user_id):
  """
  Create a new user entity and save
  Look up account with account_id and use in reference when creating new user 
  """
  account_entity = memcache_db.get_entity(account_id, "Accounts")
  
  user_key= get_user_key(account_id, user_id)
  new_user = Users(key_name=user_key,
                   userid=user_id,
                   isEnabled="yes",
                   accountRef=account_entity)
  
  try:
    memcache_db.save_entity(new_user, user_key)
  except:
    logging.error("Error saving new user entity")
    return  
  
def get_account_from_user(user_ref):
  acc = None
  if user_ref:
    try:
      if user_ref.accountRef:
        acc = user_ref.accountRef
        if not acc.isEnabled:
          logging.error("User accessing disabled account for %s"%acc.key().name())
    except:
      logging.error("User reference with key %s lacks an account"%user_ref.key().name())
  return acc

def get_user_key(account_id, user_id):
  """
  We have to have the user key so that when a widget request comes in
  the user and account info are not attainable from just the hash 
  """
  return hashlib.sha1(account_id + '---' + user_id).hexdigest()


def get_user_with_key(user_key):
  user_ref = None
  try:
    user_ref = memcache_db.get_entity(user_key, "Users")
  except:
    logging.error("Error getting key %s"%\
          (user_key))
    return None
  return user_ref

def get_or_create_user(account_id, user_id, acc_ref):
  """
  Create the user if it doesnt exist
  """
  user_ref = get_user(account_id, user_id)
  if not user_ref:
    # insert a new user, but lacking optional fields
    user_key= get_user_key(account_id, user_id)
    new_user = Users(key_name=user_key,
                     userid=user_id,
                     isEnabled="yes",
                     accountRef=acc_ref)
    try:
      memcache_db.save_entity(new_user, user_key)
    except:
      logging.error("Error saving user with key %s, userid %s for account %s"%\
             (user_key, user_id, account_id))
      return None
    user_ref = get_user(account_id, user_id)
    if not user_ref:
      logging.error("Error getting user with key %s, userid %s for account %s"%\
           (user_key, user_id, account_id))
      return None
  return user_ref

def save_user(user_ref, user_key):
  return memcache_db.save_entity(user_ref, user_key)

def update_user(user_key, dict, incr_fields):
  return memcache_db.update_fields(user_key, "Users", fields=dict, increment_fields=incr_fields)

def delete_user(user_key):
  user_ref = get_user_with_key(user_key)
  if not user_ref:
    logging.error("Unable to get user with key: " + str(user_key))
    return 

  badges = badges_dao.get_user_badges(user_ref)
  for b in badges:
    badges_dao.delete_badge_instance(b.key().name())

  return memcache_db.delete_entity_with_key(user_key, "Users")

def set_user_points(account_id, user_id, points):
  fields = {"points" : points}
  user_key = get_user_key(account_id, user_id)
  return memcache_db.update_fields(user_key, "Users", fields)
 
