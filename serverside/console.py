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
Created on Feb 1, 2011

@author: shan

Console class that will render the user console and provide additional functionality if needed.
'''
import webapp2
from google.appengine.ext.webapp import template
from google.appengine.api import mail
from google.appengine.ext import blobstore 

from serverside import constants
from serverside.session import Session
from serverside.tools.utils import account_login_required
from serverside.tools.utils import format_integer
from serverside.dao import widgets_dao
from serverside.dao import badges_dao
from serverside.dao import accounts_dao
from serverside import messages
from serverside import environment
from serverside.dao import users_dao
from serverside import notifier
from client_tools.python.userinfuser import ui_api 

# TODO This needs to be moved to users_dao
from serverside.entities.users import Users
import datetime
import hashlib
import logging
import wsgiref.handlers
import random
import json

def getErrorString(err):
  if err == "BadImageType":
    return "You may only have png, jpg, or gif image types"
  elif err == "FileTooLarge":
    return "Sorry, max image size allowed is " + str(constants.MAX_BADGE_SIZE) + " bytes"
  elif err == "InvalidID":
    return "Please check your values and try again"
  elif err == "BadBadge":
    return "Please check your badge id and try again"
  elif err == "NoUserID":
    return "A User ID was not provided, please try again"
  return err

class Console(webapp2.RequestHandler):
  @account_login_required
  def get(self):
    """ Render dashboard """
    current_session = Session().get_current_session(self)
    
    account = current_session.get_account_entity()
    api_key = account.apiKey
    
    template_values = {'dashboard_main' : True,
                       'account_name': current_session.get_email(),
                       'api_key': api_key}
    self.response.out.write(template.render(constants.TEMPLATE_PATHS.CONSOLE_DASHBOARD, template_values))

class ConsoleUsers(webapp2.RequestHandler):
  @account_login_required
  def get(self):
    """ Render users template """
    current_session = Session().get_current_session(self)
    email = current_session.get_email()
    error = self.request.get("error")
    has_error = False
    if error:
      has_error = True 
      error = getErrorString(error)
    email = current_session.get_email()
    account = current_session.get_account_entity()
    badges = badges_dao.get_rendereable_badgeset(account)
    template_values = {'users_main': True,
                       'account_name': email,
                       'badges':badges,
                       'has_error': has_error,
                       'error': error}
    self.response.out.write(template.render(constants.TEMPLATE_PATHS.CONSOLE_DASHBOARD, template_values))

class ConsoleBadges(webapp2.RequestHandler):
  @account_login_required
  def get(self):
    current_session = Session().get_current_session(self)
    email = current_session.get_email()
    account = current_session.get_account_entity()
    error = self.request.get("error")
    has_error = False
    if error:
      has_error = True 
      error = getErrorString(error)
    badgeset = badges_dao.get_rendereable_badgeset(account)
    upload_url = blobstore.create_upload_url('/badge/u')
    template_values = {'badges_main': True,
                       'account_name': email,
                       'badges': badgeset,
                       'upload_url': upload_url,
                       'has_error': has_error,
                       'error': error}
    self.response.out.write(template.render(constants.TEMPLATE_PATHS.CONSOLE_DASHBOARD, template_values))

class ConsoleEditUser(webapp2.RequestHandler):
  @account_login_required
  def get(self):
    """
    Verify that specified user exists for given account
    """
    current_session = Session().get_current_session(self)
    email = current_session.get_email()
    edit_user = self.request.get("name")
    error = self.request.get("error")
    has_error = False
    if error:
      has_error = True 
      error = getErrorString(error)
    
    """ Generate links to see each widget for user """
    userhash = hashlib.sha1(email + '---' + edit_user).hexdigest()
    
    trophy_case_widget_url = "/api/1/getwidget?widget=trophy_case&u=" + userhash
    points_widget_url = "/api/1/getwidget?widget=points&u=" + userhash
    rank_widget_url = "/api/1/getwidget?widget=rank&u=" + userhash 
    milestones_widget_url = "/api/1/getwidget?widget=milestones&u=" + userhash 
    
    template_values = {'users_edit' : True,
                       'account_name' : current_session.get_email(),
                       'editusername': edit_user,
                       'view_trophy_case':trophy_case_widget_url,
                       'view_points':points_widget_url,
                       'view_rank':rank_widget_url,
                       'view_milestones':milestones_widget_url,
                       'error':error,
                       'has_error':has_error}
    self.response.out.write(template.render(constants.TEMPLATE_PATHS.CONSOLE_DASHBOARD, template_values))

class ConsoleUsersFetch(webapp2.RequestHandler):
  @account_login_required
  def get(self):
    """ Params page, limit """
    page = self.request.get("page")
    limit = self.request.get("limit")
    order_by = self.request.get("orderby")
    
    if page == None or page == "" or limit == None or page == "":
      self.response.out.write("Error")
      return
      
    try:
      page = int(page)
      limit = int(limit)
    except:
      self.response.out.write("Error, args must be ints. kthxbye!")
      return
      
    current_session = Session().get_current_session(self)
    
    asc = "ASC"
    if order_by == "points":
      asc = "DESC"
    
    offset = page*limit
    users = users_dao.get_users_by_page_by_order(current_session.get_account_entity(), offset, limit, order_by, asc)
    
    ret_json = "{ \"users\" : ["
    first = True
    for user in users:
      """ Do not send down anonymous user to be displayed """
      if user.userid == constants.ANONYMOUS_USER:
        continue
      
      if not first:
        ret_json += ","
      first = False
      ret_json += "{"
      ret_json += "\"userid\" : \"" + user.userid + "\","
      ret_json += "\"points\" : \"" + str(user.points) + "\","
      ret_json += "\"rank\" : \"" + str(user.rank) + "\""
      ret_json += "}"
    ret_json+= "]}"
    
    self.response.out.write(ret_json)
    
  
class ConsoleFeatures(webapp2.RequestHandler):
  @account_login_required
  def get(self):
    current_session = Session().get_current_session(self)
    account = current_session.get_account_entity()
    email = current_session.get_email()
    
    """ Get widgets values """
    trophy_case_values = widgets_dao.get_trophy_case_properties_to_render(account)
    rank_values = widgets_dao.get_rank_properties_to_render(account)
    points_values = widgets_dao.get_points_properties_to_render(account)
    leaderboard_values = widgets_dao.get_leaderboard_properties_to_render(account)
    notifier_values = widgets_dao.get_notifier_properties_to_render(account)
    milestones_values = widgets_dao.get_milestones_properties_to_render(account)
    
    """ Preview urls """
    trophy_case_preview_url = ""
    rank_preview_url = ""
    points_preview_url = ""
    
    """ Notifier """
    if environment.is_dev():
      widget_path = constants.CONSOLE_GET_WIDGET_DEV
    else:
      widget_path = constants.CONSOLE_GET_WIDGET_PROD 
    widget_type = "notifier"
    userhash = hashlib.sha1(email + '---' + constants.ANONYMOUS_USER).hexdigest()
    notifier_str = "<div style='z-index:9999; overflow: hidden; position: fixed; bottom: 0px; right: 10px;'><iframe style='border:none;' allowtransparency='true' height='"+str(constants.NOTIFIER_SIZE_DEFAULT)+"px' width='"+str(constants.NOTIFIER_SIZE_DEFAULT)+"px' scrolling='no' src='" + widget_path + "?widget=" + widget_type + "&u=" + userhash + "&height=" +str(constants.NOTIFIER_SIZE_DEFAULT) + "&width="+str(constants.NOTIFIER_SIZE_DEFAULT)+"'>Sorry your browser does not support iframes!</iframe></div>"
    
    template_values = {'features_main' : True,
                       'account_name' : current_session.get_email(),
                       'trophy_case_values' : trophy_case_values,
                       'rank_values':rank_values,
                       'points_values':points_values,
                       'notifier_values': notifier_values,
                       'milestones_values': milestones_values,
                       'leaderboard_values':leaderboard_values,
                       'trophy_case_preview_url':trophy_case_preview_url,
                       'rank_preview_url':rank_preview_url,
                       'points_preview_url':points_preview_url,
                       'notifier': notifier_str}
    self.response.out.write(template.render(constants.TEMPLATE_PATHS.CONSOLE_DASHBOARD, template_values))  

class ConsoleFeaturesUpdate(webapp2.RequestHandler):
  @account_login_required
  def post(self):
    """ Ajax call handler to save trophycase features """
    current_session = Session().get_current_session(self)
    
    property = self.request.get("property")
    new_value = self.request.get("propertyValue")
    entity_type = self.request.get("entityType")
    success = widgets_dao.update_widget_property(current_session.get_email(), entity_type, property, new_value)
    
    if success:
      self.response.out.write("Success")
    else:
      self.response.out.write("Failed")

class ConsoleFeaturesPreview(webapp2.RequestHandler):
  @account_login_required
  def get(self):
    """ Ask for which widget, and then render that widget """
    widget = self.request.get("widget")
    current_session = Session().get_current_session(self)
    account = current_session.get_account_entity()
    
    if widget == "rank":
      widget_ref = account.rankWidget
      render_path = constants.TEMPLATE_PATHS.RENDER_RANK
    elif widget == "points":
      widget_ref = account.pointsWidget
      render_path = constants.TEMPLATE_PATHS.RENDER_POINTS
    elif widget == "leaderboard":
      widget_ref = account.leaderWidget
      render_path = constants.TEMPLATE_PATHS.RENDER_LEADERBOARD
    elif widget == "notifier":
      widget_ref = account.notifierWidget
      render_path = constants.TEMPLATE_PATHS.RENDER_NOTIFIER
    elif widget == "milestones":
      widget_ref = account.milestoneWidget
      render_path = constants.TEMPLATE_PATHS.RENDER_MILESTONES
    else:
      widget = "trophycase"
      widget_ref = account.trophyWidget
      render_path = constants.TEMPLATE_PATHS.RENDER_TROPHY_CASE  
      
    values = {"status":"success"}
    properties = widget_ref.properties()
    for property in properties:
      values[property] = getattr(widget_ref, property)
    
    
    show_with_data = self.request.get("withdata")
    if(show_with_data == "yes"):
      """ add appropriate dummy data """
      if widget == "trophycase":
        values["badges"] = self.getDummyBadges()
      elif widget == "rank":
        values["rank"] = str(format_integer(random.randint(1,1000)))
      elif widget == "points":
        values["points"] = str(format_integer(random.randint(1,10000)))
      elif widget == "leaderboard":
        pass
      elif widget == "notifier":
        pass
      elif widget == "milestones":
        pass  
      
    
    self.response.out.write(template.render(render_path, values))
  
  def getDummyBadges(self):
    """ Will return set of badges to be used for preview """
    badgeset = []
    for i in range(6):
      item = {"resource": "FakeResource-" + str(i),
              "downloadLink": "/images/badges/test"+str(i)+".png",
              "reason": "Reason" + str(i),
              "awardDate": datetime.datetime.now().strftime("%Y-%m-%d")}
      badgeset.append(item)
    return badgeset
  
class ConsoleFeaturesGetValue(webapp2.RequestHandler):
  @account_login_required
  def get(self):
    """ Sleep here... on PROD we hare having race condition, try this out... """
    import time
    time.sleep(0.6)
    
    """ Look up value of "of" """
    current_session = Session().get_current_session(self)
    requested_value = self.request.get("of")
    entity_type = self.request.get("entityType")
    value = widgets_dao.get_single_widget_value(current_session.get_email(), entity_type, requested_value)
    self.response.out.write(value)
    

class ConsoleAnalytics(webapp2.RequestHandler):
  @account_login_required
  def get(self):
    current_session = Session().get_current_session(self)
    template_values = {'analytics_main' : True,
                       'account_name' : current_session.get_email()}
    self.response.out.write(template.render(constants.TEMPLATE_PATHS.CONSOLE_DASHBOARD, template_values))

class ConsoleDownloads(webapp2.RequestHandler):
  @account_login_required
  def get(self):
    current_session = Session().get_current_session(self)
    template_values = {'downloads_main' : True,
                       'account_name' : current_session.get_email()}
    self.response.out.write(template.render(constants.TEMPLATE_PATHS.CONSOLE_DASHBOARD, template_values))
    
class ConsolePreferences(webapp2.RequestHandler):
  @account_login_required
  def get(self):
    """ handler for change password template """
    current_session = Session().get_current_session(self)
    template_values = {'preferences_main' : True,
                       'account_name' : current_session.get_email()}
    self.response.out.write(template.render(constants.TEMPLATE_PATHS.CONSOLE_DASHBOARD, template_values))
    
  @account_login_required
  def post(self):
    """ will handle change of password request, will return success/fail """
    current_session = Session().get_current_session(self)
    email = current_session.get_email()
    
    old_password = self.request.get("oldpassword")
    new_password = self.request.get("newpassword")
    new_password_again = self.request.get("newpasswordagain")
    
    error_message = ""
    success = False
    if new_password != new_password_again:
      error_message = "Passwords do not match."
    else:
      """ Make sure that the account authenticates... this is a redundant check """
      if accounts_dao.authenticate_web_account(email, old_password):
        changed = accounts_dao.change_account_password(email, new_password)
        if changed:
          success = True
      else:
        error_message = "Old password incorrect."
  
    template_values = {"preferences_main" : True,
                       "password_change_attempted" : True,
                       'account_name' : email,
                       "error_message": error_message,
                       "password_changed" : success}
    self.response.out.write(template.render(constants.TEMPLATE_PATHS.CONSOLE_DASHBOARD, template_values))

class ConsoleForgottenPassword(webapp2.RequestHandler):
  def get(self):
    """ handle forgotten password request """
    self.response.out.write(template.render(constants.TEMPLATE_PATHS.CONSOLE_FORGOTTEN_PASSWORD, None))

  def post(self):
    """ email posted, send a temporary password there """
    email = self.request.get("email")
    new_password = accounts_dao.reset_password(email)
    
    logging.info("Trying reset email to: " + str(email) + " temp password: " + str(new_password))
    success = False
    if new_password:
      """ send an email with new password """
      try:
        mail.send_mail(sender="UserInfuser <" + constants.APP_OWNER_EMAIL + ">",
                         to=email,
                         subject="UserInfuser Password Reset",
                         body= messages.get_forgotten_login_email(new_password))
        success = True
      except:
        logging.error("FAILED to send password reset email to: " + email)
        pass
    else:
      logging.error("Error for reset email to: " + str(email) + " temp password: " + str(new_password))
       
    values = {"success" : success,
              "response" : True}
    self.response.out.write(template.render(constants.TEMPLATE_PATHS.CONSOLE_FORGOTTEN_PASSWORD, values))
    
class ConsoleSignUp(webapp2.RequestHandler):
  def get(self):
    self.response.out.write(template.render(constants.TEMPLATE_PATHS.CONSOLE_SIGN_UP, None))
    
class ConsoleNotifierPreview(webapp2.RequestHandler):
  @account_login_required
  def get(self):
    current_session = Session().get_current_session(self)
    account_entity = current_session.get_account_entity()
    email = account_entity.email
    
    """ notify anonymous account """
    
    userhash = hashlib.sha1(email + '---' + constants.ANONYMOUS_USER).hexdigest()
    user_ref = users_dao.get_user_with_key(userhash)
    
    notifier.user_badge_award(user_ref, "Preview Message", "/images/badges/test2.png", "Sample Title", account_entity, "anonymous_badge")
    self.response.out.write("done")

class ConsoleNewNotifierToken(webapp2.RequestHandler):
  @account_login_required
  def get(self):
    current_session = Session().get_current_session(self)
    account_entity = current_session.get_account_entity()
    email = account_entity.email
    
    """ Notifier """
    if environment.is_dev():
      widget_path = constants.CONSOLE_GET_WIDGET_DEV
    else:
      widget_path = constants.CONSOLE_GET_WIDGET_PROD 
    widget_type = "notifier"
    userhash = hashlib.sha1(email + '---' + constants.ANONYMOUS_USER).hexdigest()
    notifier_str = "<div style='z-index:9999; overflow: hidden; position: fixed; bottom: 0px; right: 10px;'><iframe style='border:none;' allowtransparency='true' height='"+str(constants.NOTIFIER_SIZE_DEFAULT)+"px' width='"+str(constants.NOTIFIER_SIZE_DEFAULT)+"px' scrolling='no' src='" + widget_path + "?widget=" + widget_type + "&u=" + userhash + "&height=" +str(constants.NOTIFIER_SIZE_DEFAULT) + "&width="+str(constants.NOTIFIER_SIZE_DEFAULT)+"'>Sorry your browser does not support iframes!</iframe></div>"
    self.response.out.write(notifier_str)

class ReturnUserCount(webapp2.RequestHandler):
  def get(self):
    # TODO
    self.response.out.write("800")

class DeleteUser(webapp2.RequestHandler):
  @account_login_required
  def post(self):
    current_session = Session().get_current_session(self)
    account_entity = current_session.get_account_entity()
    email = account_entity.email
    user = self.request.get("id")
    if user == constants.ANONYMOUS_USER:
      json_ret = {"success":False,
                  "reason":"Sorry, you cannot delete this special user."}
      json_ret = json.dumps(json_ret)
      self.response.out.write(json_ret)
      return 
    json_ret = {'success':True,
                'reason':'Success. User has been deleted'}
    json_ret = json.dumps(json_ret)
    user_hash = hashlib.sha1(email + '---' + user).hexdigest()
    users_dao.delete_user(user_hash)
    self.response.out.write(json_ret)

class DeleteBadge(webapp2.RequestHandler):
  @account_login_required
  def post(self):
    current_session = Session().get_current_session(self)
    account_entity = current_session.get_account_entity()
    email = account_entity.email
    bk = self.request.get("bk")
    json_ret = {'success':True,
                'reason':'Success. Badge has been deleted'}
    json_ret = json.dumps(json_ret)
    try:
      bk = badges_dao.create_badge_key_with_id(email, bk)
      badges_dao.delete_badge(bk)
    except Exception, e:
      json_ret = {'success':False,
                'reason':'Unable to remove badge' + str(e)}
    self.response.out.write(json_ret)

class AddUser(webapp2.RequestHandler):
  @account_login_required
  def post(self):
    current_session = Session().get_current_session(self)
    account_entity = current_session.get_account_entity()
    email = account_entity.email
    new_user_id = self.request.get("id")
    if new_user_id == constants.ANONYMOUS_USER:
      self.redirect('/adminconsole/users?error=NoUserID')
      return 
    profile_name = self.request.get("name")
    profile_link = self.request.get("profile")
    profile_img = self.request.get("image")
    user_key = users_dao.get_user_key(email, new_user_id)
 
    new_user = Users(key_name=user_key,
                     userid=new_user_id,
                     isEnabled="yes",
                     accountRef=account_entity,
                     profileName=profile_name,
                     profileLink=profile_link,
                     profileImg=profile_img)
    users_dao.save_user(new_user, user_key)
    self.redirect('/adminconsole/users')

class AwardUser(webapp2.RequestHandler):
  @account_login_required
  def post(self):
    current_session = Session().get_current_session(self)
    account_entity = current_session.get_account_entity()
    email = account_entity.email
    ui = ui_api.UserInfuser(email, account_entity.apiKey, sync_all=True)

    user_id = self.request.get('userid')
    if not user_id:
      self.redirect('/adminconsole/users?error=NoUserID')
      return
    if user_id == constants.ANONYMOUS_USER:
      self.redirect('/adminconsole/users?error=InvalidID')
      return 
    if not users_dao.get_user(email, user_id):
      self.redirect('/adminconsole/users?error=InvalidID')
      return 
    award_type = self.request.get('awardtype')
    if award_type == 'awardbadge':
      badge_id = self.request.get("badgeid")
      if not badge_id:
        logging.error("Badge ID not provided %s"%email)
        self.redirect('/adminconsole/users?error=BadBadge')
      badge_key = badges_dao.get_key_from_badge_id(email, badge_id)
      if not badges_dao.get_badge(badge_key):
        logging.error("Badge ID does not exist for account %s"%email)
        self.redirect('/adminconsole/users?error=BadBadge')
      if not ui.award_badge(user_id, badge_id):
        self.redirect('/adminconsole/users?error=BadBadge')
        logging.error("Make sure the client code urls points to http://<app-id>.appspot.com if this is a custom deploy")
        logging.error("Account %s is unable to award badge %s to user %s"%(email, badge_id, user_id))
        self.redirect('/adminconsole/users?error=BadBadge')
    elif award_type == 'awardpoints': 
      points = self.request.get("points")
      try:
        points = int(points)
      except:
        points = 0
      if not ui.award_points(user_id, points):
        logging.error("Account %s is unable to award points %d to user %s"%(email, points, user_id))
        self.redirect('/adminconsole/users?error=InvalidID')
    else:
      logging.error("Received %s for console user award from account %s"%(award_type, email))
      self.redirect('/adminconsole/users?error=InvalidID')
      
    self.redirect('/adminconsole/users/edit?name=' + user_id)


app = webapp2.WSGIApplication([
  ('/adminconsole', Console),
  ('/adminconsole/users', ConsoleUsers),
  ('/adminconsole/users/edit', ConsoleEditUser),
  ('/adminconsole/users/count', ReturnUserCount),
  ('/adminconsole/users/fetch', ConsoleUsersFetch),
  ('/adminconsole/users/delete', DeleteUser),
  ('/adminconsole/users/award', AwardUser),
  ('/adminconsole/users/add', AddUser),
  ('/adminconsole/downloads', ConsoleDownloads),
  ('/adminconsole/features', ConsoleFeatures),
  ('/adminconsole/features/update', ConsoleFeaturesUpdate),
  ('/adminconsole/features/preview', ConsoleFeaturesPreview),
  ('/adminconsole/features/getvalue', ConsoleFeaturesGetValue),
  ('/adminconsole/badges', ConsoleBadges),
  ('/adminconsole/deletebadge', DeleteBadge),
  ('/adminconsole/preferences', ConsolePreferences),
  ('/adminconsole/forgot', ConsoleForgottenPassword),
  ('/adminconsole/signup', ConsoleSignUp),
  ('/adminconsole/analytics', ConsoleAnalytics),
  ('/adminconsole/notify', ConsoleNotifierPreview),
  ('/adminconsole/newnotifytoken', ConsoleNewNotifierToken)
], debug=constants.DEBUG)

"""
def main():
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
"""
