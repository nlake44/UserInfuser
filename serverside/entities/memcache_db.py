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
This is an interface to the datastore which uses memcache as a cache for
faster access.
"""
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.datastore import entity_pb
from serverside import constants
from serverside.entities.accounts import Accounts
from serverside.entities.users import Users
from serverside.entities.badges import Badges
from serverside.entities.badges import BadgeInstance
from serverside.entities.badges import BadgeImage
from serverside.entities.widgets import TrophyCase
from serverside.entities.widgets import Notifier
from serverside.entities.widgets import Milestones 
from serverside.entities.widgets import Points
from serverside.entities.widgets import Leaderboard
from serverside.entities.widgets import Rank
from serverside.entities.passphrase import PassPhrase
import logging
"""
Function:
  get_entity
Args:
  key_name
Description:
  Uses memcache to access entities in string format. Then they are converted 
  to db.Model type. If not in memcache, get it from the datastore.
Returns:
  The db.Model of the entity
"""
def get_entity(key_name, ent_type):
  if ent_type not in constants.PROTECTED_DB_TYPES:
    raise Exception()
  e = memcache.get(key=key_name, namespace=ent_type)
  if e:
    try:
      e = deserialize(e)
    except:
      logging.error("Memcache_db: Unable to deserialize entity of type %s"%ent_type)
      e = None 

  if not e:
    memcache.delete(key=key_name, namespace=ent_type)
    if ent_type == "Accounts":
      e = Accounts.get_by_key_name(key_name)
    elif ent_type == "Badges":
      e = Badges.get_by_key_name(key_name)
    elif ent_type == "BadgeInstance":
      e = BadgeInstance.get_by_key_name(key_name)
    elif ent_type == "BadgeImage":
      e = BadgeImage.get_by_key_name(key_name)
    elif ent_type == "Users":
      e = Users.get_by_key_name(key_name)
    elif ent_type == "TrophyCase":
      e = TrophyCase.get_by_key_name(key_name)
    elif ent_type == "Points":
      e = Points.get_by_key_name(key_name)
    elif ent_type == "Notifier":
      e = Notifier.get_by_key_name(key_name)
    elif ent_type == "Rank":
      e = Rank.get_by_key_name(key_name)
    elif ent_type == "PassPhrase":
      e = PassPhrase.get_by_key_name(key_name)
    elif ent_type == "Milestones":
      e = Milestones.get_by_key_name(key_name)
    elif ent_type == "Leaderboard":
      e = Leaderboard.get_by_key_name(key_name)
    else:
      raise Exception()
    if e:
      memcache.add(key=key_name,value=str(serialize(e)),namespace=ent_type)
  return e

"""
TODO : Need to think if this is even possible. Can base it on a timeout, 
and it caches the last 1 minute or something...
"""
def __run_query(query, ent_type):
  return

"""
Function:
  batch_get_entity
Args:
  key_name list
Description:
  Uses memcache to access entities in string format. Then they are converted 
  to db.Model type. If not in memcache, get it from the datastore. This function
  gets a batch of keys at once, first from memcache, and the remaining from 
  the db in parallel. Only deals with one type.
Returns:
  List of db.Model of the entity

Experimental
TODO NEEDS TESTING
"""
def __batch_get_entity(key_names, ent_type):
  if ent_type not in constants.PROTECTED_DB_TYPES:
    raise Exception()
  es = memcache.get_multi(keys=key_names, namespace=ent_type)
  ents = []
  db_ents = {}
  for key in key_names:
    e = None
    if key in es:
      try:
        e = deserialize(e) 
        ents.append(e)
      except Exception, ex:
        logging.error("Memcache_db: Unable to deserialize entity of type %s with %s"%(ent_type, str(ex)))
        e = None
    if not e:
      # These puts are in a loop, making this function slow
      memcache.delete(key=key, namespace=ent_type)
      if ent_type == "Accounts":
        dbent = Accounts.get_by_key_name(key)
        ents.append(dbebt)
        db_ents[key] = serialize(dbent)
      elif ent_type == "Badges":
        dbent = Badges.get_by_key_name(key)
        ents.append(dbebt)
        db_ents[key] = serialize(dbent)
      elif ent_type == "BadgeInstance":
        dbent = BadgeInstance.get_by_key_name(key)
        ents.append(dbebt)
        db_ents[key] = serialize(dbent)
      elif ent_type == "BadgeImage":
        dbent = BadgeImage.get_by_key_name(key)
        ents.append(dbebt)
        db_ents[key] = serialize(dbent)
      elif ent_type == "Users":
        dbent = Users.get_by_key_name(key)
        ents.append(dbebt)
        db_ents[key] = serialize(dbent)
      elif ent_type == "TrophyCases":
        dbent = TrophyCases.get_by_key_name(key)
        ents.append(dbebt)
        db_ents[key] = serialize(dbent)
      else:
        raise Exception()
  memcache.set_multi(mapping=db_ents,namespace=ent_type)
  return ents

"""
Function
  update_fields
Args:
  fields: A dictionary of what to update
  key_name: the key to the entity 
  ent_type
  increment_fields: A dictionary but incremented by given ammount. 
                    This number can also be negative
Returns:
  The Key object of the entity
"""
def update_fields(key_name, ent_type, fields={}, increment_fields={}):
  if ent_type not in constants.PROTECTED_DB_TYPES:
    raise Exception()
  def _txn():
    entity = get_entity(key_name, ent_type)
    if not entity:
      raise Exception()
    if fields:
      for ii in fields:
        setattr(entity, ii, fields[ii])
    if increment_fields:
      for ii in increment_fields:
        prev_val = getattr(entity, ii) 
        if not prev_val: prev_val = 0
        setattr(entity, ii,  prev_val + increment_fields[ii])
    entity.key_name = key_name
    ret = entity.put()
    memcache.delete(key=key_name, namespace=ent_type)
    memcache.add(key=key_name,
                 value=str(serialize(entity)),
                 namespace=ent_type)
    return ret
  ret = db.run_in_transaction(_txn)
  return ret

"""
Function:
  save_entity 
Args:
  entity
  key_name
  ent_type
Description:
  For first time creation of an entity to be placed in memcache & DB
Returns:
  The Key object of the entity
"""
def save_entity(ent, key_name):
  if not ent:
    raise Exception()
  ent_type  = ent.__class__.__name__
  if ent_type not in constants.PROTECTED_DB_TYPES:
    logging.error("Memcache_db: Type %s not valid"%ent_type)
    raise Exception()
  def _txn():
    memcache.delete(key=key_name, namespace=ent_type)
    ent.key_name = key_name
    ret = ent.put()
    if ret:
      memcache.add(key=key_name , value=str(serialize(ent)), namespace=ent_type)
    return ret
  return db.run_in_transaction(_txn)

"""
Function:
  delete_entity 
Args:
  entity
  key_name
  ent_type
Raises:
  If deleting on a non-exiting ent, NotSavedError is raised   
"""
def delete_entity(ent, key_name):
  if not ent:
    raise Exception()
  ent_type = ent.__class__.__name__
  if ent_type not in constants.PROTECTED_DB_TYPES:
    raise Exception()
  memcache.delete(key=key_name, namespace=ent_type)
  ret = ent.delete() 
  return ret

"""
Function:
  delete_entity_with_key
Args:
  key_name
  ent_type
Raises:
  Nothing
"""
def delete_entity_with_key(key_name, ent_type):
  key = db.Key.from_path(ent_type, key_name)
  memcache.delete(key=key_name, namespace=ent_type)
  ret = db.delete(key) 
  return ret 

""" Serialization and deserialization of models """
def serialize(models):
  if models is None:
    return None
  elif isinstance(models, db.Model):
    # Just one instance
    return db.model_to_protobuf(models).Encode()
  else:
    # A list
    return [db.model_to_protobuf(x).Encode() for x in models]
 
def deserialize(data):
  if data is None:
    return None
  elif isinstance(data, str):
  # Just one instance
    return db.model_from_protobuf(entity_pb.EntityProto(data))
  else:
    return [db.model_from_protobuf(entity_pb.EntityProto(x)) for x in data]

def is_in_memcache(key_name, ent_type):
  e = memcache.get(key=key_name, namespace=ent_type)
  if e: return True
  else: return False

def is_in_db(key_name, ent_type):
  if ent_type not in constants.PROTECTED_DB_TYPES:
    raise Exception()
  e = None
  if ent_type == "Accounts":
    e = Accounts.get_by_key_name(key_name)
  elif ent_type == "Badges":
    e = Badges.get_by_key_name(key_name)
  elif ent_type == "BadgeInstance":
    e = BadgeInstance.get_by_key_name(key_name)
  elif ent_type == "BadgeImage":
    e = BadgeInstance.get_by_key_name(key_name)
  elif ent_type == "Users":
    e = Users.get_by_key_name(key_name)
  elif ent_type == "TrophyCases":
    e = TrophyCase.get_by_key_name(key_name)
  else:
    raise Exception()

  if e: return True
  else: return False

 
