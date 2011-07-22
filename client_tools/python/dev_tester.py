# Copyright (C) 2011, CloudCaptive
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

import os
import time
import sys
import inspect
from userinfuser.ui_api import *
from userinfuser.ui_constants import *
pwd = os.getcwd()
# Test to make sure it can read the API key from the env
prime_path = "http://localhost:8080/api/1/test"
delete_path = "http://localhost:8080/api/1/testcleanup"
IS_LOCAL = True
# ID settings for testing
account = "test@test.c"
testId = "testuserid"
testId2 = "anotheruser"
testId3 = "anotheruserxxxx"
badgeId1 = "music-1-private"
badgeId2 = "music-2-private"
badgeId3 = "music-3-private"
badgeId9 = "music-9-private"

testSecret = "8u8u9i9i"
# Set API key
apiKey = "ABCDEFGHI"
DEFAULT_DEBUG = True
# Turn this off/on to leave or delete data from the db 
cleanup = False
def __url_post(url, argsdic):
  import urllib
  import urllib2
  import socket
  socket.setdefaulttimeout(30) 
  if argsdic:
    url_values = urllib.urlencode(argsdic)

  req = urllib2.Request(url, url_values)
  response = urllib2.urlopen(req)
  output = response.read()

  return output  

""" Make sure what we received is what we expected """
def checkerr(line_num, received, expected):
  if expected != received:
    print "Failed for test at " + sys.argv[0] + ": " + str(line_num) + \
          " with a return of: " + str(received) + " while expecting: " + str(expected)
    exit(1)

""" Make sure the item is not what we received """
def notcheckerr(line_num, received, shouldnotbe):
  if shouldnotbe == received:
    print "Failed for test at " + sys.argv[0] + ": " + str(line_num) \
        + " with a return of: " + str(received) + \
        " while it should not be but was: " + str(shouldnotbe)
    exit(1)

""" See if the given string is contained in the response """
def checkstr(line_num, received, searchstr):
  if searchstr not in str(received):
    print "Failed for test at " + sys.argv[0] + ":" + str(line_num) \
        + " with a return of: " + str(received) + \
        " while searching for: " + searchstr
    exit(1)

""" See if the given string is not contained in the response """
def checknotstr(line_num, received, searchstr):
  if searchstr not in received:
    return
  else:
    print "Failed for test at " + sys.argv[0] + ":" + str(line_num) \
        + " with a return of: " + str(received) + \
        " while searching for: " + searchstr + " where it should not be"
    exit(1)
      
def lineno():
  return inspect.currentframe().f_back.f_lineno

ui_good = UserInfuser(account, apiKey, debug=DEFAULT_DEBUG, local=IS_LOCAL, sync_all=True)
ui_bad = UserInfuser(account, apiKey + "x", debug=DEFAULT_DEBUG, local=IS_LOCAL, sync_all=True)
badgetheme1 = "music"
badgetheme2 = "birds"

# Prime the DB with an account and badges
argsdict = {"apikey":apiKey,
           "accountid":account,
           "badgeid":badgeId1,
           "secret":testSecret,
           "user":testId,
           "theme":badgetheme1}

ret = __url_post(prime_path, argsdict)
checkstr(lineno(), ret, "success")
ret = __url_post(delete_path, argsdict)
checkstr(lineno(), ret, "success")
ret = __url_post(prime_path, argsdict)
checkstr(lineno(), ret, "success")

# ADD USER TESTS
start = time.time()
checkerr(lineno(), ui_good.update_user(testId, "Raaaaaaj", "http://facebook.com/nlake44", "http://imgur.com/AK9Fw"), True)
end = time.time()
sync_time = end - start
success = True
try:
  success = ui_bad.update_user(testId, "Heather", "http://www.facebook.com/profile.php?id=710661131", "http://profile.ak.fbcdn.net/hprofile-ak-snc4/203293_710661131_7132437_n.jpg")
except ui_errors.PermissionDenied:
  success = False
checkerr(lineno(), success, False)   

# Add a new field because we did not do it before
checkerr(lineno(), ui_good.update_user(testId, user_name="Raj", link_to_profile="http://facebook.com/nlake44", link_to_profile_img="http://profile.ak.fbcdn.net/hprofile-ak-snc4/203059_3610637_6604695_n.jpg"), True)
success = True
try:
  success = ui_bad.update_user(testId, user_name="Jack Smith", link_to_profile="http://test.com/a", link_to_profile_img="http://test.com/a/image")
except ui_errors.PermissionDenied:
  success = False
checkerr(lineno(), success, False)   

success = True
try:
  success = ui_good.update_user(testId2, user_name="Billy Gene", link_to_profile="http://www.facebook.com/isnotmylove", link_to_profile_img="http://cdn3.iconfinder.com/data/icons/faceavatars/PNG/J01.png")
except ui_errors.BadArgument:
  success = False
checkerr(lineno(), success, True)   


# AWARD BADGE TESTS
checkerr(lineno(), ui_good.award_badge(testId, badgeId1, reason="Star Power"), True)
success = True
try:
  success = ui_bad.award_badge(testId, badgeId1, reason="Star User")
except ui_errors.PermissionDenied:
  success = False
checkerr(lineno(), success, False)   
success = True
try:
  success = ui_good.award_badge(testId, "", reason="Promoter")
except ui_errors.BadArgument:
  success = False
checkerr(lineno(), success, False)   

success = True
try:
  success = ui_good.award_badge(testId, badgeId1 + "xxx", reason="Star Power")
except ui_errors.BadgeDoesNotExist:
  success = False
checkerr(lineno(), success, False)   


checkerr(lineno(), ui_good.award_badge(testId, badgeId2, reason='Maven'), True)
success = True
try:
  success =ui_bad.award_badge(testId, badgeId2, reason="For Fun")
except ui_errors.PermissionDenied:
  success = False
checkerr(lineno(), success, False)   

checkerr(lineno(), ui_good.remove_badge(testId, badgeId3), True)
checknotstr(lineno(), str(ui_good.get_user_data(testId)), badgeId3)
checkerr(lineno(), ui_good.award_badge_points(testId, badgeId3, 10, 100, reason="Power User"), True)
checkerr(lineno(), ui_good.award_badge_points(testId, badgeId3, 10, 100, reason="Power User"), True)
checkerr(lineno(), ui_good.award_badge_points(testId, badgeId3, 10, 100, reason="Power User"), True)
checknotstr(lineno(), str(ui_good.get_user_data(testId)), badgeId3)
checkerr(lineno(), ui_good.award_badge_points(testId, badgeId3, 70, 100, reason="Power User"), True)
checkstr(lineno(), str(ui_good.get_user_data(testId)), badgeId3)
success = True
try:
  success =ui_bad.award_badge(testId, badgeId2, reason="Shooting Star")
except ui_errors.PermissionDenied:
  success = False
checkerr(lineno(), success, False)   


# GET WIDGET TESTS
checkstr(lineno(), ui_good.get_widget(testId, "trophy_case"), "trophy_case")
checkstr(lineno(), ui_good.get_widget(testId, "milestones"), "milestones")
checkstr(lineno(), ui_good.get_widget(testId, "points"), "points")
checkstr(lineno(), ui_good.get_widget(testId, "rank"), "rank")
checkstr(lineno(), ui_good.get_widget(testId, "notifier"), "notifier")
checkstr(lineno(), ui_good.get_widget(testId, "leaderboard"), "leaderboard")

print ui_good.get_widget(testId, "trophy_case")
print ui_good.get_widget(testId, "points")
print ui_good.get_widget(testId, "rank")
print ui_good.get_widget(testId, "notifier")
print ui_good.get_widget(testId, "leaderboard")
success = True
try:
  success =ui_good.get_widget(testId, "doesnotexit")
except ui_errors.UnknownWidget:
  success = False
checkerr(lineno(), success, False)

# AWARD POINTS TESTS
checkerr(lineno(), ui_good.award_points(testId, 100, "just because"),True)
checkerr(lineno(), ui_good.award_points(testId, 100, "just because"),True)
success = True
try:
  success =ui_bad.award_points(testId, 100, "just because")
except ui_errors.PermissionDenied:
  success = False
checkerr(lineno(), success, False)   

success = True
try:
  success = ui_good.award_points(testId, "xxx", "just because")
except ui_errors.BadArgument:
  success = False
checkerr(lineno(), success, False)   

# GET USER DATA TESTS
# Verify badges are correctly being queried for
checkstr(lineno(), str(ui_good.get_user_data(testId)), badgeId1)
checkstr(lineno(), str(ui_good.get_user_data(testId)), badgeId2)
checkstr(lineno(), str(ui_good.get_user_data(testId)), testId)
# Check to see if points was incremented correctly
checkstr(lineno(), str(ui_good.get_user_data(testId)), "200")
success =  ui_bad.get_user_data(testId)
checkstr(lineno(), success, "failed")   

badUser = "blahblahblah___"
success =  ui_good.get_user_data(badUser)
checkstr(lineno(), success, "failed")

if cleanup:
  checkerr(lineno(), ui_good.remove_badge(testId, badgeId1), True)
  checkerr(lineno(), ui_good.remove_badge(testId, badgeId2), True)
  checkerr(lineno(), ui_good.remove_badge(testId, badgeId3), True)

success = True
try:
  success = ui_good.remove_badge(testId, "-x-x-x" + badgeId3 + "xxx" )
except ui_errors.BadgeDoesNotExist:
  success = False
checkerr(lineno(), success, False)   

#Delete the DB badges with an account and badges
ret = __url_post(delete_path, argsdict)
checkstr(lineno(), ret, "success")
###################################
# Async testing
###################################
ui_good = UserInfuser(account, apiKey, debug=DEFAULT_DEBUG, local=True)
ui_bad = UserInfuser(account, apiKey + "x", debug=DEFAULT_DEBUG, local=True)
ret = __url_post(delete_path, argsdict)
checkstr(lineno(), ret, "success")
ret = __url_post(prime_path, argsdict)
checkstr(lineno(), ret, "success")

# ADD USER TESTS
start = time.time()
checkerr(lineno(), ui_good.update_user(testId, user_name="Raj", link_to_profile="http://facebook.com/nlake44", link_to_profile_img="http://imgur.com/AK9Fw"), True)
end = time.time()
async_time = end - start
if async_time > sync_time:
  print "Async calls are slower than sync calls???"
  print "Async time: " + str(async_time)
  print "Sync time:" + str(sync_time)
  exit(1)
# async calls dont throw anything, always return true
success = ui_bad.update_user(testId, "a", "http://test.com/a", "http://test.com/a/image")
checkerr(lineno(), success, True)   

# Add a new field because we did not do it before
checkerr(lineno(), ui_good.update_user(testId, user_name="Jakob", link_to_profile="http://profile.ak.fbcdn.net/hprofile-ak-snc4/49299_669633666_9641_n.jpg", link_to_profile_img="http://profile.ak.fbcdn.net/hprofile-ak-snc4/49299_669633666_9641_n.jpg"), True)
# will return true
success = ui_bad.update_user(testId, user_name="Jack Smith", link_to_profile="http://test.com/a", link_to_profile_img="http://test.com/a/image")
checkerr(lineno(), success, True)

success = ui_good.update_user(testId2, user_name="Shan", link_to_profile="http://www.facebook.com/profile.php?id=3627076", link_to_profile_img="http://www.facebook.com/album.php?profile=1&id=3627076")
checkerr(lineno(), success, True)


# AWARD BADGE TESTS
# all calls should return true
checkerr(lineno(), ui_good.award_badge(testId, badgeId1, reason="Bright"), True)
success =  ui_bad.award_badge(testId, badgeId1, reason="For Fun")
checkerr(lineno(), success, True)
success = ui_good.award_badge(testId, "", reason="Star Power")
checkerr(lineno(), success, True)   

success = ui_good.award_badge(testId, badgeId1 + "xxx", reason="Celeb Status")
checkerr(lineno(), success, True)


success = ui_bad.award_badge(testId, badgeId2, reason="For fun")
checkerr(lineno(), success, True)

checkerr(lineno(), ui_good.remove_badge(testId, badgeId3), True)
# enough time to catch up
time.sleep(1)
checknotstr(lineno(), str(ui_good.get_user_data(testId)), badgeId3)
checkerr(lineno(), ui_good.award_badge_points(testId, badgeId3, 10, 100, reason="Star Power"), True)
time.sleep(1)
checkerr(lineno(), ui_good.award_badge_points(testId, badgeId3, 10, 100, reason="Star Power"), True)
time.sleep(1)
checkerr(lineno(), ui_good.award_badge_points(testId, badgeId3, 10, 100, reason="Star Power"), True)
time.sleep(1)
checknotstr(lineno(), str(ui_good.get_user_data(testId)), badgeId3)
checkerr(lineno(), ui_good.award_badge_points(testId, badgeId3, 70, 100, reason="Lobster Bisque mmmm"), True)
checkerr(lineno(), ui_good.award_badge_points(testId, badgeId3, 70, 100, reason="ice cream sandwiches"), True)
checkerr(lineno(), ui_good.award_badge_points(testId, badgeId3, 70, 100, reason="Good Times"), True)

# partial award
checkerr(lineno(), ui_good.award_badge_points(testId, badgeId9, 10, 100, reason="Almost there"), True)

time.sleep(2)
checkstr(lineno(), str(ui_good.get_user_data(testId)), badgeId3)
success = ui_bad.award_badge(testId, badgeId2, reason="For fun")
checkerr(lineno(), success, True)

checkerr(lineno(), ui_good.award_badge(testId, badgeId2, reason="Shooting High"), True)

# GET WIDGET TESTS
checkstr(lineno(), ui_good.get_widget(testId, "trophy_case"), "trophy_case")
checkstr(lineno(), ui_good.get_widget(testId, "milestones"), "milestones")
checkstr(lineno(), ui_good.get_widget(testId, "notifier"), "notifier")
checkstr(lineno(), ui_good.get_widget(testId, "points"), "points")
checkstr(lineno(), ui_good.get_widget(testId, "rank"), "rank")


# AWARD POINTS TESTS
checkerr(lineno(), ui_good.award_points(testId, 100, "just because"),True)
checkerr(lineno(), ui_good.award_points(testId, 100, "just because"),True)
success = ui_bad.award_points(testId, 100, "just because")
checkerr(lineno(), success, True)

success = ui_good.award_points(testId, "xxx", "just because")
checkerr(lineno(), success, True)

# GET USER DATA TESTS
# Verify badges are correctly being queried for
time.sleep(1)
checkstr(lineno(), str(ui_good.get_user_data(testId)), badgeId1)
checkstr(lineno(), str(ui_good.get_user_data(testId)), badgeId2)
checkstr(lineno(), str(ui_good.get_user_data(testId)), testId)
# Check to see if points was incremented correctly
checkstr(lineno(), str(ui_good.get_user_data(testId)), "200")

if cleanup:
  checkerr(lineno(), ui_good.remove_badge(testId, badgeId1), True)
  checkerr(lineno(), ui_good.remove_badge(testId, badgeId2), True)
  checkerr(lineno(), ui_good.remove_badge(testId, badgeId3), True)

success = ui_good.remove_badge("-x-x-x" + badgeId3 + "xxx", testId)
checkerr(lineno(), success, True)   
#ui_good.sync_all = True
success = ui_good.update_user(testId2, user_name="Raj", link_to_profile="http://www.facebook.com/nlake44", link_to_profile_img="http://profile.ak.fbcdn.net/hprofile-ak-snc4/203059_3610637_6604695_n.jpg")
checkstr(lineno(), ui_good.get_widget(testId2, "rank"), "rank")
ui_good.award_points(testId2, 10)
checkerr(lineno(), ui_good.update_user(testId3), True)
ui_good.create_badge("apple","oranges","fruit", "http://cdn1.iconfinder.com/data/icons/Futurosoft%20Icons%200.5.2/128x128/apps/limewire.png")
ui_good.award_badge("testuserid", "oranges-apple-private", reason="FRUIT!")
checkerr(lineno(), ui_good.award_badge_points(testId, "music-4-private", 10, 100, reason="Power User"), True)
time.sleep(1)

# award partial badge points 
#Delete the DB badges with an account and badges
if cleanup:
  ret = __url_post(delete_path, argsdict)
  checkstr(lineno(), ret, "success")
  # clear out the second user
  argsdict['user'] = testId2
  ret = __url_post(prime_path, argsdict)
  ret = __url_post(delete_path, argsdict)
  checkstr(lineno(), ret, "success")
  argsdict['user'] = testId3
  ret = __url_post(prime_path, argsdict)
  ret = __url_post(delete_path, argsdict)
  checkstr(lineno(), ret, "success")

print ui_good.get_widget(testId, "trophy_case")
print ui_good.get_widget(testId, "milestones")
print ui_good.get_widget(testId, "points")
print ui_good.get_widget(testId, "rank")
print ui_good.get_widget(testId, "notifier")
print ui_good.get_widget(testId, "leaderboard")
 
# Need to test awarding a badge via points
print "SUCESS" 
exit(0)

