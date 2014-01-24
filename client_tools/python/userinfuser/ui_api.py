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

import json
import os 
import hashlib
import ui_constants
import ui_errors
import threading
import urllib
import urllib2

try:
  # For GAE
  from google.appengine.api import urlfetch
  import logging
except:
  pass

def ui_threaded(callback=lambda *args, **kwargs: None, daemonic=True):
  """Decorate a function to run in its own thread and report the result
  by calling callback with it. Code yanked from stackoverflow.com"""
  def innerDecorator(func):
    def inner(*args, **kwargs):
      target = lambda: callback(func(*args, **kwargs))
      t = threading.Thread(target=target)
      t.setDaemon(daemonic)
      t.start()
    return inner
  return innerDecorator



class UserInfuser():
  def __init__(self, 
               account, # required 
               api_key, # required
               debug=False, 
               local=False, 
               encrypt=True,
               sync_all=False):
    """ 
      Constructor
      Required Arguments: 
                 account_email: The email you registered with
                 api_key: The key provided by UserInfuser
      Optional Arguments: 
                 encrypt: To Enable HTTPS (secure connections)
                 debug: For debugging information
                 local: Used for testing purposes
                 sync_all: Make all calls synchronous (slows your 
                           application down, only use it for testing)
      Exception: Tosses a BadConfiguration if required arguments are None
    """
    self.ui_url =  ui_constants.UI_PATH
    if encrypt:
      self.ui_url = ui_constants.UI_SPATH

    self.isGAE = False
    try:
      # There is no threading in Google App Engine
      from google.appengine.api import urlfetch
      self.isGAE = True
      # URL Fetch is not async in the dev server, force to sync
      if os.environ["SERVER_SOFTWARE"].find("Development") != -1:
        self.ui_url = ui_constants.LOCAL_TEST
        self.debug_log("Local testing enabled")
        self.raise_exceptions = True
    except:
      pass

    self.sync_all = sync_all

    self.debug = debug
    self.debug_log("debug is on, account: %s, apikey: %s"%(account, api_key))
    
    self.api_key = api_key
    if not account or not api_key:
      raise ui_errors.BadConfiguration()
    self.account = account

    self.raise_exceptions = ui_constants.RAISE_EXCEPTIONS
    if local:
      self.ui_url = ui_constants.LOCAL_TEST
      self.debug_log("Local testing enabled")
      self.raise_exceptions = True

    self.update_user_path = self.ui_url + ui_constants.API_VER + "/" + \
                         ui_constants.UPDATE_USER_PATH
    self.award_badge_path = self.ui_url + ui_constants.API_VER + "/" +\
                         ui_constants.AWARD_BADGE_PATH
    self.award_badge_points_path = self.ui_url + ui_constants.API_VER + "/"+\
                         ui_constants.AWARD_BADGE_POINTS_PATH
    self.award_points_path = self.ui_url + ui_constants.API_VER + "/"+\
                         ui_constants.AWARD_POINTS_PATH
    self.get_user_data_path = self.ui_url + ui_constants.API_VER + "/" + \
                         ui_constants.GET_USER_DATA_PATH
    self.remove_badge_path = self.ui_url + ui_constants.API_VER + "/" + \
                         ui_constants.REMOVE_BADGE_PATH
    self.widget_path = self.ui_url + ui_constants.API_VER + "/" + \
                         ui_constants.WIDGET_PATH
    self.create_badge_path = self.ui_url + ui_constants.API_VER + "/" + \
                         ui_constants.CREATE_BADGE_PATH
    
    self.timeout = 10 # seconds

  def get_user_data(self, user_id):
    """
     Function: get_user_data
     Arguments: user_id
                The user id is a unique identifier. It could be an email or 
                unique name. 
     Return value: Returns a dictionary of information about the user
           example:
           {"status": "success", 
            "is_enabled": "yes", 
            "points": 200, 
            "user_id": "nlake44@gmail.com", 
            "badges": ["muzaktheme-guitar-private", 
                       "muzaktheme-bass-private", 
                       "muzaktheme-drums-private"], 
            "profile_img": "http://test.com/images/raj.png",
            "profile_name": "Raj Chohan", 
            "profile_link": "http://test.com/nlake44", 
            "creation_date": "2011-02-26"} 
     Notes: This function is always synchronous. It will add latency into 
            your application/web site.
    """
    argsdict = {"apikey":self.api_key,
               "userid":user_id,
               "accountid":self.account}
    ret = '{"status":"failed"}'
    try:
      ret = self.__url_post(self.get_user_data_path, argsdict)
      self.debug_log("Received: %s"%ret)
    except:
      self.debug_log("Connection Error")
      if self.raise_exceptions:
        raise ui_errors.ConnectionError()

    try:
      ret = json.loads(ret) 
    except:
      self.debug_log("Unable to parse return message")
    return ret
  
  def update_user(self, user_id, user_name="", link_to_profile="", link_to_profile_img=""):
    """
     Function: update_user
     Description: To either add a new user, or update a user's information
     Required Arguments: user_id (unique user identifier)
     Optional Arguments: 
                user_name (The name that will show up in widgets, otherwise it
                           will use the user_id)
                link_to_profile (a URL to the user's profile)
                link_to_profile (a URL to a user's profile picture)
     Return value: True on success, False otherwise
    """
    argsdict = {"apikey":self.api_key,
               "userid":user_id,
               "accountid":self.account,
               "profile_name":user_name,
               "profile_link": link_to_profile,
               "profile_img":link_to_profile_img}
    ret = None
    try:
      if self.sync_all:
        ret = self.__url_post(self.update_user_path, argsdict)
      else: 
        self.__url_async_post(self.update_user_path, argsdict)
        return True
      self.debug_log("Received: %s"%ret)
    except:
      self.debug_log("Connection Error")
      if self.raise_exceptions:
        raise ui_errors.ConnectionError()
    return self.__parse_return(ret)


  def award_badge(self, user_id, badge_id, reason="", resource=""):
    """
     Function: award_badge
     Description: Award a badge to a user
     Required Arguments: user_id (unique user identifier)
                         badge_id (unique badge identifier from 
                                   UserInfuser website under badges tab of 
                                   control panel)
     Optional Arguments: reason (A short string that shows up in the user's 
                                 trophy case)
                         resource (A URL that the user goes to if the badge 
                                 is clicked) 
     Return value: True on success, False otherwise
    """
    argsdict = {"apikey":self.api_key,
               "accountid":self.account,
               "userid":user_id,
               "badgeid":badge_id,
               "resource": resource,
               "reason":reason}
    ret = None
    try:
      if self.sync_all:
        ret = self.__url_post(self.award_badge_path, argsdict)
      else: 
        self.__url_async_post(self.award_badge_path, argsdict)
        return True
      self.debug_log("Received: %s"%ret)
    except:
      self.debug_log("Connection Error")
      if self.raise_exceptions:
        raise ui_errors.ConnectionError()
    return self.__parse_return(ret)

  def remove_badge(self, user_id, badge_id):
    """
     Function: remove_badge
     Description: Remove a badge from a user
     Required Arguments: user_id (unique user identifier)
                         badge_id (unique badge identifier from 
                                   UserInfuser website under badges tab of 
                                   control panel)
     Return value: True on success, False otherwise
    """ 

    argsdict = {"apikey":self.api_key,
               "accountid":self.account,
               "userid":user_id,
               "badgeid":badge_id}
    ret = None
    try:
      if self.sync_all:
        ret = self.__url_post(self.remove_badge_path, argsdict)
      else: 
        self.__url_async_post(self.remove_badge_path, argsdict)
        return True
      self.debug_log("Received: %s"%ret)
    except:
      self.debug_log("Connection Error")
      if self.raise_exceptions:
        raise ui_errors.ConnectionError()
    return self.__parse_return(ret)

  def award_points(self, user_id, points_awarded, reason=""):
    """
     Function: award_points
     Description: Award points to a user
     Required Arguments: user_id (unique user identifier)
                         points_awarded 
     Optional Arguments: reason (Why they got points)
     Return value: True on success, False otherwise
    """ 
    argsdict = {"apikey":self.api_key,
               "accountid":self.account,
               "userid":user_id,
               "pointsawarded":points_awarded,
               "reason":reason}
    ret = None
    try:
      if self.sync_all:
        ret = self.__url_post(self.award_points_path, argsdict)
      else: 
        self.__url_async_post(self.award_points_path, argsdict)
        return True
      self.debug_log("Received: %s"%ret)
    except:
      self.debug_log("Connection Error")
      if self.raise_exceptions:
        raise ui_errors.ConnectionError()
    return self.__parse_return(ret)

  def award_badge_points(self, user_id, badge_id, points_awarded, points_required, reason="", resource=""):
    """
     Function: award_badge_points
     Description: Award badge points to a user. Badges can also be achieved
                  after a certain number of points are given towards an 
                  action. When that number is reached the badge is awarded to
                  the user. 
     Required Arguments: user_id (unique user identifier)
                         points_awarded 
                         badge_id (unique badge identifier from 
                                   UserInfuser website under badges tab of 
                                   control panel)
                         points_required (The total number of points a user must
                                   collect to get the badge)
     Optional Arguments: reason (Why they got the badge points)
                         resource (URL link to assign to badge)
     Return value: True on success, False otherwise
    """
    argsdict = {"apikey":self.api_key,
               "accountid":self.account,
               "userid":user_id,
               "badgeid":badge_id,
               "pointsawarded":points_awarded,
               "pointsrequired":points_required,
               "reason":reason, 
               "resource":resource}
    ret = None
    try:
      if self.sync_all:
        ret = self.__url_post(self.award_badge_points_path, argsdict)
      else: 
        self.__url_async_post(self.award_badge_points_path, argsdict)
        return True
      self.debug_log("Received: %s"%ret)
    except:
      self.debug_log("Connection Error")
      if self.raise_exceptions:
        raise ui_errors.ConnectionError()
      return False

    return self.__parse_return(ret)

 
  def get_widget(self, user_id, widget_type, height=500, width=300):
    """
     Function: get_widget
     Description: Retrieve the HTML 
     Required Arguments: user_id (unique user identifier)
                         widget_type (Check website for supported widgets)
     Optional Arguments: height and width. It is strongly recommended to tailor 
                         these values to your site rather than using the default
                         (500x300 pixels). Wigets like points and rank should
                         be much smaller.
     Return value: String to place into your website. The string will render an 
                   iframe of a set size. Customize your widgets on the
                   UserInfuser website.
    """
    if not user_id:
      user_id = ui_constants.ANONYMOUS
    if widget_type not in ui_constants.VALID_WIDGETS:
      raise ui_errors.UnknownWidget()
    userhash = hashlib.sha1(self.account + '---' + user_id).hexdigest()
    self.__prefetch_widget(widget_type, user_id)
    if widget_type != "notifier":
      return "<iframe border='0' z-index:9999; frameborder='0' height='"+str(height)+"px' width='"+str(width)+"px' allowtransparency='true' scrolling='no' src='" + self.widget_path + "?widget=" + widget_type + "&u=" + userhash + "&height=" +str(height) + "&width="+str(width)+"'>Sorry your browser does not support iframes!</iframe>"
    else:
      return "<div style='z-index:9999; overflow: hidden; position: fixed; bottom: 0px; right: 10px;'><iframe style='border:none;' allowtransparency='true' height='"+str(height)+"px' width='"+str(width)+"px' scrolling='no' src='" + self.widget_path + "?widget=" + widget_type + "&u=" + userhash + "&height=" +str(height) + "&width="+str(width)+"'>Sorry your browser does not support iframes!</iframe></div>"

  @ui_threaded()
  def __threaded_url_post(self, url, argsdic):
    self.__url_post(url, argsdic)  

  def __url_async_post(self, url, argsdic):
    if self.isGAE:
      # This will not work on the dev server for GAE, dev server must only use
      # synchronous calls
      rpc = urlfetch.create_rpc(deadline=10)
      try:
        urlfetch.make_fetch_call(rpc, url, payload=urllib.urlencode(argsdic), method=urlfetch.POST)
      except:
        self.debug_log("Unable to make fetch call to url: %s"%url)
    else:
      self.__threaded_url_post(url, argsdic)
 
  def __url_post(self, url, argsdic):
    try:
      import socket
      socket.setdefaulttimeout(self.timeout)
    except:
      pass  
    url_values = ""
    if argsdic:
      url_values = urllib.urlencode(argsdic)
  
    req = urllib2.Request(url, url_values)
    output = ""
    if self.isGAE:
      try:
        output = urlfetch.fetch(url=url, 
                                payload=url_values, 
                                method=urlfetch.POST,
                                deadline=10)
        output = output.content
      except:
        self.debug_log("Exception tossed when opening url: %s"%url)
        output =""
    else:
      try:
        response = urllib2.urlopen(req)
        output = response.read()
      except:
        self.debug_log("Exception tossed when opening url: %s"%url)
        output = "" 

    self.debug_log("urllib output %s"%output)
  
    return output  

  def __parse_return(self, ret):
    try:
      ret = json.loads(ret) 
    except:
      self.debug_log("Unable to parse return message")
      return False
    
    if ret['status'] == 'failed':
      self.debug_log(ret['error'])
      if self.raise_exceptions:
        error_code = int(ret['errcode'])
        raise ui_errors.ui_error_map[error_code]()
      return False
    return True

  def __prefetch_widget(self, widget_type, user_id):
    """ Prefetch the widget for the user """
    argsdict = {"apikey":self.api_key,
               "accountid":self.account,
               "userid":user_id,
               "widget":widget_type}
    try:
      self.__url_async_post(self, self.widget_path, argsdict)
    except:
      pass

  def create_badge(self, badge_name, badge_theme, description, link):
    """ Hidden Menu APIs """
    """ Badges should be created using the console """
    argsdict = {"apikey":self.api_key,
               "accountid":self.account,
               "name":badge_name,
               "theme":badge_theme,
               "description":description,
               "imagelink":link}
    ret = None
    try:
      ret = self.__url_post(self.create_badge_path, argsdict)
    except:
      self.debug_log("Connection Error")
      if self.raise_exceptions:
        raise ui_errors.ConnectionError()
    return self.__parse_return(ret)


  def debug_log(self, message):
    if not self.debug:
      return
    if self.isGAE:
      logging.info(message) 
    else:
      print(message)

