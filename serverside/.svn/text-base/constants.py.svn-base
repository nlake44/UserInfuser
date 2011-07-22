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
import os

# CHANGE THIS FOR CUSTOMER DEPLOYMENTS 
APP_NAME = "cloudcaptive-userinfuser" #os.environ['APPLICATION_ID']
APP_OWNER_EMAIL = "raj@cloudcaptive.com"

# Only valid for localhost testing
# Sign up twice with these accounts to get around the email validation
TEST_ACCOUNTS = ["raj@cloudcaptive.com","shanrandhawa@gmail.com","shan@cloudcaptive.com"]

ADMIN_ACCOUNT = "admin@" + APP_NAME + ".appspot.com"
DEBUG = True
ACCOUNT_TYPES = ["admin", "bronze", "silver", "gold", "platinum"]
PAYMENT_TYPES = ["free", "trial", "paid", "exempt"]
DEV_URL = "http://localhost:8080"
PRODUCTION_URL= "http://"+APP_NAME+".appspot.com"
SECURE_PRODUCTION_URL = "https://"+APP_NAME+".appspot.com"


"""
Use the following constants for generating widget previews on the admin console
These are API constants.
"""
CONSOLE_GET_WIDGET_DEV = "http://localhost:8080/api/1/getwidget"
CONSOLE_GET_WIDGET_PROD = "https://"+APP_NAME+".appspot.com/api/1/getwidget"


AES_ENCRYPTION_KEYNAME = "aes_encryption_key"
ENCRYPTION_KEYNAME = "encryption_key"

""" These are types which can not use the db methods directly and must
    use the memcache interface in serverside.entities.memcache_db. 
    These entities are used frequently and are thus memcached aggressively
    All others types may freely use the db.Model functions
"""
PROTECTED_DB_TYPES = ["Accounts", "Badges", "Users", "BadgeInstance", "BadgeImage", "TrophyCase", "Milestones", "Points", "Notifier", "Rank", "Leaderboard", "PassPhrase"]

class LOGGING:
  """ Logging events """
  CLIENT_EVENT = ["signin",
             "logout",
             "dropaccount",
             "startpayments",
             "upgrade",
             "downgrade",
             "dropuser",
             "addbadge",
             "removebadge",
             "error",
             "viewanalytics",
             "viewbadges",
             "signup",
             "test"]

  API_EVENT = ["awardpoints",
             "awardbadge",
             "awardbadgepoints",
             "badgeawarded", # if required badge points met
             "removebadge",
             "viewwidget",
             "prefetchwidget",
             "clickbadge",
             "updateuser",
             "loginuser",
             "createuser",
             "getuserdata",
             "notify_badge",
             "notify_points"]

  # Actual key is generated the first time the application is launched
  SECRET_KEYNAME = "secret_log_key"
  PATH = '/logevents'

class UPDATE:
  SECRET_KEYNAME = "secret_update_key"
  PATH = '/updateaccount'

class IMAGE_PARAMS:
  DEFAULT_SIZE = 150
  LEADER_SIZE = 90 
  VALID_EXT_TYPES = ['png','jpg','jpeg','gif','PNG','JPG','JPEG','GIF']
  # TODO Host these ourselves
  USER_AVATAR = "http://i.imgur.com/cXhDa.png"
  POINTS_IMAGE = "http://cdn1.iconfinder.com/data/icons/nuove/128x128/actions/edit_add.png"
  LOGIN_IMAGE = "http://www.iconfinder.com/icondetails/8794/128/cryptography_key_lock_log_in_login_password_security_icon" 

class API_ERROR_CODES:
  NOT_AUTH = 1 # Not authorized error, either bad account or api key
  BADGE_NOT_FOUND = 2
  USER_NOT_FOUND = 3
  INTERNAL_ERROR = 4 
  BAD_ARGS = 5
  BAD_USER = 6

class ACCOUNT_STATUS:
  """Enum(ish) of account status"""
  
  ENABLED = "enabled"
  PENDING_CREATE = "pending_create"
  DISABLED = "disabled"
  RANGE_OF_VALUES = [ENABLED,
                     PENDING_CREATE,
                     DISABLED]

class TEMPLATE_PATHS:
  CONSOLE_LOGIN = os.path.join(os.path.dirname(__file__), '../static/console_templates/login.html')
  CONSOLE_FORGOTTEN_PASSWORD = os.path.join(os.path.dirname(__file__), '../static/console_templates/forgot.html')
  CONSOLE_DASHBOARD =  os.path.join(os.path.dirname(__file__), '../static/console_templates/dashboard.html')
  CONSOLE_USERS =  os.path.join(os.path.dirname(__file__), '../static/console_templates/users.html')
  CONSOLE_SIGN_UP =  os.path.join(os.path.dirname(__file__), '../static/console_templates/signup_console.html')
  
  RENDER_TROPHY_CASE = os.path.join(os.path.dirname(__file__), 'api/widgets/v1.0/trophy_case.html')
  RENDER_NOTIFIER = os.path.join(os.path.dirname(__file__), 'api/widgets/v1.0/notifier.html')
  RENDER_MILESTONES = os.path.join(os.path.dirname(__file__), 'api/widgets/v1.0/milestones.html')
  RENDER_POINTS = os.path.join(os.path.dirname(__file__), 'api/widgets/v1.0/points.html')
  RENDER_RANK = os.path.join(os.path.dirname(__file__), 'api/widgets/v1.0/rank.html')
  RENDER_LEADERBOARD = os.path.join(os.path.dirname(__file__), 'api/widgets/v1.0/leaderboard.html')

class WEB_ADMIN_PARAMS:
  """Several standardized parameters used to keep track of authentication and sessions on web """
  COOKIE_EMAIL_PARAM = "key" # simply email, however, we don't want people their address is set in the cookie
  COOKIE_KEY_PARAM = "ssid" # same as the cookie_key param in our Accounts DB
  COOKIE_EXPIRATION = "esid" # expiration
  VALID_FOR_SECONDS = 86400 # make session valid for a day 

class WEB_SIGNUP_URLS:
  """Since we want to mask appspot from the URL we cannot have redirects to relative paths when deployed"""
  POST_DATA = ""
  ACTIVATE_URL = ""
  REDIRECT_SIGNUP_SUCCESS = ""
  REDIRECT_SIGNUP_FAIL = ""
  REDIRECT_ACTIVATE_SUCCESS = ""
  REDIRECT_ACTIVATE_FAIL = ""
  REDIRECT_HOME = ""
  REDIRECT_SIGNUP = ""
  
  if os.environ["SERVER_SOFTWARE"].find("Development") != -1:
    POST_DATA = "/signup"
    ACTIVATE_URL = "/signup"
    REDIRECT_SIGNUP_SUCCESS = "/html/signup_success.html"
    REDIRECT_SIGNUP_FAIL = "/html/signup_failed.html"
    REDIRECT_ACTIVATE_SUCCESS = "/html/activation_success.html"
    REDIRECT_ACTIVATE_FAIL = "/html/activation_fail.html"
    REDIRECT_HOME = "/html/index.html"
    REDIRECT_SIGNUP = "/html/signup.html"
  else:
    POST_DATA = SECURE_PRODUCTION_URL + "/signup" # need to use https URL for posting credentials
    ACTIVATE_URL = SECURE_PRODUCTION_URL + "/signup"
    REDIRECT_SIGNUP_SUCCESS = PRODUCTION_URL + "/html/signup_success.html"
    REDIRECT_SIGNUP_FAIL = PRODUCTION_URL + "/html/signup_failed.html"
    REDIRECT_ACTIVATE_SUCCESS = PRODUCTION_URL + "/html/activation_success.html"
    REDIRECT_ACTIVATE_FAIL = PRODUCTION_URL + "/html/activation_fail.html"
    REDIRECT_HOME = PRODUCTION_URL + "/html/index.html"
    REDIRECT_SIGNUP = PRODUCTION_URL + "/html/signup.html"
  
  

# This is only for localhost testing, not valid for production
ADMINPASSWD = "u8u8u9i9i"
ADMINKEY = "u8u89i9i"

VALID_WIDGETS = ["trophy_case", "notifier", "milestones", "points", "leaderboard", "rank"]
WIDGETS_THAT_DONT_NEED_A_USER = ["milestones", "leaderboard"]
ANONYMOUS_USER = "__ui__anonymous__"
LOCAL_URL = "http://localhost:8080/"
MAX_BADGE_SIZE = 2<<16 # 128k
NOTIFIER_SIZE_DEFAULT = 180
NOT_RANKED = -1 # For unranked users
NUMBER_RANKED = "10000" #Anyone not in the top 10k is not ranked
TOP_USERS = "10"

