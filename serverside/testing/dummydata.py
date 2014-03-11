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

@author: shan
'''
import webapp2

from serverside.dao import accounts_dao
from serverside.dao import users_dao
from serverside.entities.counter import *
import random

class CreateDummyAccountsAndUsers(webapp2.RequestHandler):
  def get(self):
    """
    Generate several accounts and users to test out stuff with
    """
    
    for i in range(10):
      """
      create 10 accounts
      """
      email = "user" + str(i) + "@infuser.com"
      account_entity = accounts_dao.create_account(email, "1111", True)
      
      for j in range(random.randint(40,100)):
        """
        create 40-100 users per account
        """
        user_id = "crazy" + str(i) + "crazy" + str(j) + "@someplaceelse" + str(i) + ".com"
        users_dao.create_new_user(email, user_id)
        users_dao.set_user_points(email, user_id, random.randint(5,200))
        
    self.response.out.write("Done. :-)")

class CreateDummyBatchData(webapp2.RequestHandler):
  def get(self):      
    # yesterday 
    import datetime
    import random
     
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)
    tomorrow = today + datetime.timedelta(days=1) 
    account_key = "test@test.c"
    badges = ["theme-name-private", "theme2-name-private", "theme3-name-private"]
    for kk in range(365):
      for bid in badges:
        rand = random.randint(0,300)
        b = BadgePointsBatch(date=today + datetime.timedelta(days=kk),
                           badgeid=bid,
                           account_key=account_key,
                           counter=rand)
        b.put()
        rand = random.randint(0,300)
        b = BadgeBatch(date=today + datetime.timedelta(days=kk),
                           badgeid=bid,
                           account_key=account_key,
                           counter=rand)
        b.put()
    for kk in range(365):
      ii = 0
      rand = random.randint(0,300)
      b = APICountBatch(date=today + datetime.timedelta(days=kk),
                       account_key=account_key,
                       counter=rand)
      b.put()
      rand = random.randint(0,300)
      b = PointBatch(date=today + datetime.timedelta(days=kk),
                       account_key=account_key,
                       counter=rand)
      b.put()


    self.response.out.write("Done. :-)")
