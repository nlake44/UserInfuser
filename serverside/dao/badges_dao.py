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
Created on Feb 28, 2011

psuedo DAO methods

@author: shan
'''
from serverside.entities.users import Users
from serverside.entities.badges import Badges
from serverside.entities.badges import BadgeInstance
from serverside.entities.badges import BadgeImage
from serverside.entities import memcache_db
from serverside import constants
from serverside import environment
from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.api import images
import logging
import string
import hashlib
import datetime

def get_full_link(relative_path):
  """ 
  Returns the full link for a given badge (dev vs production)
  """
  
  if relative_path.startswith("http"):
    # already full
    return relative_path

  if environment.is_dev():
    return constants.LOCAL_URL + relative_path
  else:
    return constants.PRODUCTION_URL + relative_path

def get_all_badges_for_account(account):
  """
  Will return all badges per the account, ordered by theme
  """
  
  return Badges.gql("WHERE creator=:1 ORDER BY theme", account)

def create_badge_key(email, badge_theme, badge_name, permission):
  if permission == "public":
    email = constants.ADMIN_ACCOUNT
  emailHash = hashlib.sha1(email).hexdigest()
  badge_key = emailHash + "-" + badge_theme + "-" + badge_name + "-" + permission
  return badge_key

def create_badge_key_with_id(email, bk_id):
  emailHash = hashlib.sha1(email).hexdigest()
  badge_key = emailHash + "-" + bk_id
  return badge_key

def create_badge_type(badge_key, 
                      badge_name, 
                      badge_des, 
                      account, 
                      badge_theme, 
                      img_type,
                      imgbuf=None,
                      blob_info=None,
                      perm="private",
                      btype="free", 
                      stype="blob", 
                      is_enabled="yes"):
  """
  Storage is either using a BadgeImage or through the blobstore api for 
  faster and cheaper serving of images
  """
  blob_key = None
  storage_type = "blob"
  badge_image = None
  download_link = ""
  if imgbuf:
    storage_type = "db"
    badge_image = create_badge_image(badge_key, perm, account, imgbuf, img_type)
    download_link = get_full_link("badge/d?bk=" + badge_key)
  elif blob_info:
    storage_type = "blob"
    blob_key = blob_info.key()  
    download_link = images.get_serving_url(str(blob_key))
    logging.info("Badge serving url:" + str(download_link))
  else:
    logging.error("Create badge type error: No image to save for badge type") 
    raise

  badge = Badges(key_name=badge_key,
                 name=badge_name,
                 altText=badge_des,
                 description=badge_des,
                 setType=btype,
                 isEnabled=is_enabled,
                 creator=account,
                 permissions=perm,
                 storageType=storage_type,
                 imageKey=badge_image,
                 blobKey=blob_key,
                 downloadLink=download_link, 
                 theme=badge_theme)
  # Store it as a badge image
  memcache_db.save_entity(badge, badge_key)
  return badge

def create_badge_instance(badge_instance_key, 
                          badge_ref, 
                          user_ref,
                          isawarded, 
                          points, 
                          points_needed, 
                          perm, 
                          link,
                          reason,
                          expiration=None):
  if isawarded == "yes":
    date = datetime.date.today()
    datet = datetime.datetime.now()
  else:
    date = None
    datet = None
  if date:
    new_badge_instance = BadgeInstance(key_name=badge_instance_key,
                                       badgeRef=badge_ref,
                                       userRef=user_ref,
                                       awarded=isawarded,
                                       pointsEarned=points,
                                       pointsRequired=points_needed,
                                       permissions=perm,
                                       downloadLink=link,
                                       reason=reason,
                                       awardDate = date,
                                       awardDateTime = datet)
  else:
    new_badge_instance = BadgeInstance(key_name=badge_instance_key,
                                       badgeRef=badge_ref,
                                       userRef=user_ref,
                                       awarded=isawarded,
                                       pointsEarned=points,
                                       pointsRequired=points_needed,
                                       permissions=perm,
                                       downloadLink=link,
                                       reason=reason)

  memcache_db.save_entity(new_badge_instance, badge_instance_key)
              
  return new_badge_instance

def create_badge_image(badge_key, perm, acc, imgbuf, img_type):
  badge_img = BadgeImage(key_name=badge_key,
                        permissions = perm,
                        creator=acc,
                        image=imgbuf,
                        imgType = img_type) 
  memcache_db.save_entity(badge_img, badge_key)
  return badge_img

def update_badge_instance(badge_key, diction, incr_fields):
  # Get the old one, and if it was just now awarded set the date/time
  if 'awarded' in diction and diction['awarded'] == "yes":
    try:
      badge_ref = memcache_db.get_entity(badge_instance_key, "BadgeInstance")
      if badge_ref and badge_ref.awarded == "no":
        diction['awardDate'] = datetime.date.today()
        diction['awardDateTime'] = datetime.datetime.now()
    except:
      diction['awardDate'] = datetime.date.today()
      diction['awardDateTime'] = datetime.datetime.now()
  return memcache_db.update_fields(badge_key, "BadgeInstance",
                         fields=diction, increment_fields=incr_fields)

def get_rendereable_badgeset(account):
  """
  Will return a badgset as follows:
  theme
   -badgeset
    name
    description
    alt
    key
    perm(issions)
  """
  badges = get_all_badges_for_account(account)
  badgeset = []
  
  for b in badges:
    """ Badge id is theme-name-perm. spaces and " " become "-" """
    name_for_id = string.replace(b.name, " ", "_")
    name_for_id = string.replace(name_for_id, "-", "_")
    
    theme_for_id = string.replace(b.theme, " ", "_")
    theme_for_id = string.replace(theme_for_id, "-", "_")
    
    badge_id = theme_for_id + "-" + name_for_id + "-" + b.permissions 
  
    item = {"name": b.name,
            "description": b.description,
            "alt":b.altText,
            "key":b.key().name(),
            "perm":b.permissions,
            "theme" : b.theme,
            "id": badge_id,
            "downloadLink":b.downloadLink}
    badgeset.append(item)
  return badgeset
    
def get_themes(account):
  """
  Will return a list with all the themes for this account
  """
  
  all_themes = Badges.gql("WHERE creator=:1", account)
  
  """ Go through the list and remove redundancies """
  theme_set = []
  previous_theme = ""
  for theme in all_themes:
    if theme.theme != previous_theme:
      theme_set.append(theme.theme)
      previous_theme = theme.theme
  
def get_badge(badge_key):
  """
  Returns the reference to a badge, otherwise logs an error
  """
  badge_ref = None
  try:
    badge_ref = memcache_db.get_entity(badge_key, "Badges")
  except:
    logging.error("badges_dao: Error getting badge type with key %s"%badge_key)
  return badge_ref
 
def get_user_badges(user_ref):
  """
  Get a user's registered badges (both awarded and not awarded)
  """
  if user_ref:
    return db.GqlQuery("SELECT * FROM BadgeInstance WHERE userRef=:1", user_ref)
  else:
    return []

def get_badge_instance_key(badge_key, user_id):
  """
  Instance keys are like badge keys but have the user id prepended
  """
  return user_id + "-" + badge_key

def get_badge_instance(badge_instance_key):
  badge_ref = None
  try:
    badge_ref = memcache_db.get_entity(badge_instance_key, "BadgeInstance")
  except:
    logging.error("badges_dao: Error getting badge type with key %s"%badge_key)
    raise
  return badge_ref

def get_key_from_badge_id(account_id, badge_id):
  """ 
  Create a badge key from an account id and badgeref
  """
  tokens = badge_id.split('-')
  if len(tokens) != 3:
    logging.error("Incorrect number of tokens during parsing. %s, for account id %s for badge %s"%\
          (str(tokens), account_id, badge_id))
    return None
  badge_theme = tokens[0]
  badge_name = tokens[1]
  perm = tokens[2]
  if perm == "public":
    email = constants.ADMIN_ACCOUNT
  elif perm == "private":
    email = account_id
  else:
    logging.error("Perm of %s for account %s and badge id of %s"%(perm, account_id, badge_id))
    return None
  return create_badge_key(email, badge_theme, badge_name, perm)

def get_badge_key_permission(badge_key):
  """
  This function works for Badges and BadgeInstance types
  """
  tokens = badge_key.split('-')
  perm = tokens[-1]
  return perm

def get_badge_id_from_instance_key(instance_key):
  return instance_key.split('-',2)[2]

def get_badge_name_from_instance_key(instance_key):
  return instance_key.split('-')[2]

def get_badge_image(badge_key):
  return memcache_db.get_entity(badge_key, "BadgeImage")

def delete_badge(badge_key):
  return memcache_db.delete_entity_with_key(badge_key, "Badges")

def delete_badge_instance(badge_instance_key): 
  return memcache_db.delete_entity_with_key(badge_instance_key, "BadgeInstance")

def delete_badge_image(badge_image_key):
  return memcache_db.delete_entity_with_key(badge_image_key, "BadgeImage")

def delete_badge_blob(badge_key):
  badge = memcache_db.get_entity(badge_key, "Badges")
  if badge.blobKey:
    blob_key = badge.blobKey
    blob = BlobInfo.get(blob_key)
    blob.delete()

def add_resource_link(badge_key, url):
  diction = {'resourceLink':url}
  return memcache_db.update_fields(badge_key, "Badges",
                         fields=diction)
    
def add_expiration(badge_key, date):
  diction = {'expiration':date}
  return memcache_db.update_fields(badge_key, "Badges",
                         fields=diction)
