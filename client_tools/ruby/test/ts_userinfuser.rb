=begin
Copyright (C) 2011 CloudCaptive

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
=end

# Programmer: Chris Bunch

$:.unshift File.join(File.dirname(__FILE__), "..", "lib")
require 'userinfuser'

$:.unshift File.join(File.dirname(__FILE__), "..", "test")
require 'test_helper'

require 'test/unit'

ACCOUNT = "test@test.c"
API_KEY = "ABCDEFGHI"

DEFAULT_DEBUG = true
NO_DEBUG = false

IS_LOCAL = true
IS_REMOTE = false

ENCRYPT = true
NO_ENCRYPT = false

SYNC_ALL = true
ASYNC_ALL = false

SECRET = "8u8u9i9i"

ID1 = "testuserid"
ID2 = "anotheruser"
ID3 = "anotheruserxxxx"

BADGEID1 = "music-1-private"
BADGEID2 = "music-2-private"
BADGEID3 = "music-3-private"
BADGETHEME = "music"

PRIME_PATH = "http://localhost:8080/api/1/test"
DELETE_PATH = "http://localhost:8080/api/1/testcleanup"

CLEANUP = false

SUCCESS = '{"status": "success"}'

PARAMS = {
  "apikey" => API_KEY,
  "accountid" => ACCOUNT,
  "badgeid" => BADGEID1,
  "secret" => SECRET,
  "user" => ID1,
  "theme" => BADGETHEME
}

REASON = "just because"

def get_good_ui(sync)
  return UserInfuser.new(ACCOUNT, API_KEY, DEFAULT_DEBUG, IS_LOCAL, NO_ENCRYPT, sync)
end

def get_bad_ui(sync)
  return UserInfuser.new(ACCOUNT, API_KEY + "x", DEFAULT_DEBUG, IS_LOCAL, NO_ENCRYPT, sync)
end

require 'tc_users'
require 'tc_awardbadges'
require 'tc_getwidgets'
require 'tc_awardpoints'
require 'tc_getuserdata'

