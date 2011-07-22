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

psuedo DAO methods and data access utilities

@author: shan
'''
from serverside.entities.widgets import TrophyCase
from serverside.entities.widgets import Rank
from serverside.entities.widgets import Points
from serverside.entities.widgets import Notifier
from serverside.entities.widgets import Leaderboard
from serverside.entities.widgets import Milestones
from serverside.entities import memcache_db
from serverside.dao import accounts_dao
from serverside.tools import utils
import logging


def get_trophy_case(key):
  """
  return corresponding trophy case entity
  
  This function seems unnecesary, but later we might need to do additional checking
  An effort to standardize data access
  """  
  logging.info("retrieving trophy case for account: " + key)
  return memcache_db.get_entity(key, "TrophyCase")

def update_widget_property(email, entity_name, property_name, property_value):
  """
  Saves desired property with new value for the specified entity type
  """
  
  """
  Check to see if the value string is a number or boolean
  """
  logging.info("Try to persist value, but first find out what it is!")
  try:
    value = long(property_value)
    update_fields = { property_name : value }
    memcache_db.update_fields(email, entity_name, update_fields)
    logging.info("Seems to be a number")
    return True
  except:
    try:
      bool_value = bool(property_value)
      if property_value == "True":
        update_fields = { property_name : True }
      else:
        update_fields = { property_name : False }
      memcache_db.update_fields(email, entity_name, update_fields)
      logging.info("Seems to be a boolean")
      return True
    except:
      try:
        update_fields = { property_name : property_value }
        memcache_db.update_fields(email, entity_name, update_fields)
        logging.info("Seems to be a string")
        return True
      except:
        return False
      
      

def update_trophy_property(email, property_name, property_value):
  """
  Saves desired property with new value
  """
  
  return update_widget_property(email, "TrophyCase", property_name, property_value)

def get_single_trophy_case_value(key, value_name):
  tcase_entity = get_trophy_case(key)
  if tcase_entity != None:
    value = str(tcase_entity.__getattribute__(str(value_name)))
    if value != None:
      return value
    else:
      return "Error"
  else:
    return "Error"


def get_single_widget_value(key, entity_name, value_name):
  widget_entity = memcache_db.get_entity(key, entity_name)
  if widget_entity != None:
    value = str(widget_entity.__getattribute__(str(value_name)))
    if value != None:
      return value
    else:
      return "Error"
  else:
    return "Error"
    

def get_trophy_case_properties_to_render(email):
  return get_values("TrophyCase", email, TrophyCase.properties())

def get_rank_properties_to_render(email):
  return get_values("Rank", email, Rank.properties())

def get_points_properties_to_render(email):
  return get_values("Points", email, Points.properties())
    
def get_notifier_properties_to_render(email):
  return get_values("Notifier", email, Notifier.properties())

def get_milestones_properties_to_render(email):
  return get_values("Milestones", email, Milestones.properties())

def get_leaderboard_properties_to_render(email):
  return get_values("Leaderboard", email, Leaderboard.properties())

def create_widget_for_account_by_email(widget_name, email):
  """
  Creates a new widget for the account, will return widget object if success, else it will return None
  """
  new_widget = None
  property_name = None
  if widget_name == "TrophyCase":
    new_widget = TrophyCase(key_name=email)
    property_name = "trophyWidget"
  elif widget_name == "Rank":
    new_widget = Rank(key_name=email)
    property_name = "rankWidget"
  elif widget_name == "Points":
    new_widget = Points(key_name=email)
    property_name = "pointsWidget"
  elif widget_name == "Notifier":
    new_widget = Notifier(key_name=email)
    property_name = "notifierWidget"
  elif widget_name == "Milestones":
    new_widget = Milestones(key_name=email)
    property_name = "milestoneWidget"
  elif widget_name == "Leaderboard":
    new_widget = Leaderboard(key_name=email)
    property_name = "leaderWidget"
    
  if new_widget!= None:
    memcache_db.save_entity(new_widget, email)
    update_fields = { property_name : new_widget }
    memcache_db.update_fields(email, "Accounts", update_fields)
  else:
    logging.info("Unable to create widget because widget type unknown: " + widget_name)
    
  return new_widget

def get_widget_for_account(account, widget_name):
  ret_widget = None
  if widget_name == "TrophyCase":
    ret_widget = account.trophyWidget
  elif widget_name == "Rank":
    ret_widget = account.rankWidget
  elif widget_name == "Points":
    ret_widget = account.pointsWidget
  elif widget_name == "Notifier":
    ret_widget = account.notifierWidget
  elif widget_name == "Milestones":
    ret_widget = account.milestoneWidget
  elif widget_name == "Leaderboard":
    ret_widget = account.leaderWidget
  return ret_widget
      
def get_values(widget_entity_name, account, properties):
  """
  Utility method to generate editable values dynamically.
  Using this method is pure laziness. If we want cool drop
  downs and color pickers we need to have a static mapping
  for all fields.
  """
  
  widget_entity = get_widget_for_account(account, widget_entity_name)
  email = account.email
  
  if widget_entity == None:
    """ create the required widget here """
    widget_entity = create_widget_for_account_by_email(widget_entity_name, email)
    if(widget_entity != None):
      logging.info("Created widget " + widget_entity_name + " dynamically for account: " + email + " because one did not already exist.")
  
  if widget_entity != None:
    widget_values=[]
    for property in properties:
      logging.debug(str(property))
      logging.debug("Value: " + str(widget_entity.__getattribute__(str(property))))
      
      property_name = str(property)
      property_value = str(widget_entity.__getattribute__(str(property)))
      
      new_widget_value = WidgetValue().new_widget_value(property_name, property_value, widget_entity_name)
      widget_values.append(new_widget_value)
      
    return widget_values
  else:
    return None
  
class WidgetValue:
  """
  ID,Value objects to make rendering neater... Contains several params used in rendering
  """
  def new_widget_value(self, id, value, entity_type):
    self.id = id
    self.name = utils.camelcase_to_friendly_str(id)
    self.value = value
    
    """ Other needed params """
    self.save_id = "save_" + id + entity_type
    self.action_id = "action_" + id + entity_type
    self.input_id = "input_" + id + entity_type
    self.td_id = "td_" + id + entity_type
    return self

def delete_widget(widget_key, wtype):
  return memcache_db.delete_entity_with_key(widget_key, wtype)

def add_notifier(acc_ref):
  logging.error("Had to add a Notifier widget to an account " + str(acc_ref.key().name()))
  new_notifier = Notifier(key_name=acc_ref.key().name())
  memcache_db.save_entity(new_notifier, acc_ref.key().name())
  acc_ref.notifierWidget = new_notifier
  accounts_dao.save(acc_ref)
  return new_notifier

def add_rank(acc_ref):
  logging.error("Had to add a Rank widget to an account " + str(acc_ref.key().name()))
  new_rank= Rank(key_name=acc_ref.key().name())
  memcache_db.save_entity(new_rank, acc_ref.key().name())
  acc_ref.rankWidget = new_rank
  accounts_dao.save(acc_ref)
  return new_rank

def add_points(acc_ref):
  logging.error("Had to add a Points widget to an account " + str(acc_ref.key().name()))
  new_points= Points(key_name=acc_ref.key().name())
  memcache_db.save_entity(new_points, acc_ref.key().name())
  acc_ref.pointsWidget = new_points
  accounts_dao.save(acc_ref)
  return new_points

def add_trophy_case(acc_ref):
  logging.error("Had to add a Trophy widget to an account " + str(acc_ref.key().name()))
  new_trophy_case= TrophyCase(key_name=acc_ref.key().name())
  memcache_db.save_entity(new_trophy_case, acc_ref.key().name())
  acc_ref.trophyWidget = new_trophy_case
  accounts_dao.save(acc_ref)
  return new_trophy_case

def add_leader(acc_ref):
  logging.error("Had to add a Leader widget to an account " + str(acc_ref.key().name()))
  new_leader= Leaderboard(key_name=acc_ref.key().name())
  memcache_db.save_entity(new_leader, acc_ref.key().name())
  acc_ref.leaderWidget = new_leader
  accounts_dao.save(acc_ref)
  return new_leader

def add_milestones(acc_ref):
  logging.error("Had to add a Milestones widget to an account " + str(acc_ref.key().name()))
  new_milestones = Milestones(key_name=acc_ref.key().name())
  memcache_db.save_entity(new_milestones, acc_ref.key().name())
  acc_ref.milestonesWidget = new_milestones
  accounts_dao.save(acc_ref)
  return new_milestones

 
