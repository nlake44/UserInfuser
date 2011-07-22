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
Created on April 18, 2011

DAO methods for secrets. 
This way we generate secrets on startup and don't have to comb the code
when open sourcing it. It's a db read cost, but memcache should
amortize that cost. 

@author: Raj
'''
from serverside.entities import memcache_db
from serverside.entities.passphrase import PassPhrase
from serverside import constants
import logging
import string 
import random 
def gen_random(length):
  return ''.join(random.choice(string.letters) for i in xrange(length))
 
def get_log_secret():
  secret = memcache_db.get_entity(constants.LOGGING.SECRET_KEYNAME, "PassPhrase")
  if not secret: 
    phrase = gen_random(16)
    ent = PassPhrase(key_name=constants.LOGGING.SECRET_KEYNAME, secret=phrase)
    memcache_db.save_entity(ent, constants.LOGGING.SECRET_KEYNAME)
    return phrase
  else:
    return secret.secret

def get_update_secret():
  secret = memcache_db.get_entity(constants.UPDATE.SECRET_KEYNAME, "PassPhrase")
  if not secret: 
    phrase = gen_random(16)
    ent = PassPhrase(key_name=constants.UPDATE.SECRET_KEYNAME, secret=phrase)
    memcache_db.save_entity(ent, constants.UPDATE.SECRET_KEYNAME)
    return phrase
  else:
    return secret.secret


def get_encrypt_secret():
  secret = memcache_db.get_entity(constants.ENCRYPTION_KEYNAME, "PassPhrase")
  if not secret: 
    phrase = gen_random(8) #must be 8 characters long
    ent = PassPhrase(key_name=constants.ENCRYPTION_KEYNAME, secret=phrase)
    memcache_db.save_entity(ent, constants.ENCRYPTION_KEYNAME)
    return phrase
  else:
    return secret.secret

def get_aes_encrypt_secret():  
  secret = memcache_db.get_entity(constants.AES_ENCRYPTION_KEYNAME, "PassPhrase")
  if not secret: 
    phrase = gen_random(16) # must be 16 chars long
    ent = PassPhrase(key_name=constants.AES_ENCRYPTION_KEYNAME, secret=phrase)
    memcache_db.save_entity(ent, constants.AES_ENCRYPTION_KEYNAME)
    return phrase
  else:
    return secret.secret
