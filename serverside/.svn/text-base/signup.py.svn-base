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

from constants import ACCOUNT_STATUS
from django.utils import simplejson
from entities import memcache_db
from entities.pending_create import Pending_Create
from google.appengine.api import mail
from google.appengine.ext import webapp
from google.appengine.ext.db import NotSavedError
from google.appengine.ext.webapp import template
from serverside.dao import accounts_dao, pending_create_dao
from serverside.entities.emails import Email
from tools import utils
from tools.xss import XssCleaner
import constants
import environment
import logging
import messages
import uuid


json = simplejson

class NewsLetterSignUp(webapp.RequestHandler):
  def post(self):
    clean = XssCleaner()
    email = self.request.get('email')    
    email = clean.strip(email)
    newemail = Email(email=email)
    newemail.put()
    ret = {"success":"true"}
    ret = json.dumps(ret) 
    self.response.out.write(ret)



class SignUp(webapp.RequestHandler):
  """
  get: is used to activate an account.
  post: is used to handle sign up requests coming from web form.
  """
  
  def get(self):
    """Account activation via email"""
    
    values = {'error_message' : "Activation not successful.",
              'error': True}
    
    id = self.request.get("activate")
    error_message = self.request.get("error_msg") 
    if id == None or id == "":
      if error_message:
        values['error_message'] = error_message
      logging.error("Activation attempted without ID")
    else:
      """Look up the account in pending creates table"""
      try:
        pending_entity = Pending_Create.get_by_key_name(id)
        account = None
        if pending_entity != None:
          """ Look up corresponding account entity """
          email = pending_entity.email
          account = memcache_db.get_entity(email, "Accounts")
        else:
          logging.error("Pending entity could not be looked up.")
          
        if account != None:
          if account.isEnabled == ACCOUNT_STATUS.PENDING_CREATE:
            update_fields = {"isEnabled" : ACCOUNT_STATUS.ENABLED }
            memcache_db.update_fields(email, "Accounts", update_fields)
            
            try:
              """ remove item from pending creates """
              pending_entity.delete()
            except NotSavedError:
              logging.error("Entity with id: " + id + " was not in data store...")
              
            values = {'activation' : True}
          else:
            logging.error("Account status is not pending create")
            
      except:
        logging.error("Activation tried and failed with ID: " + id)
    
    """ render with values set above """
    self.response.out.write(template.render(constants.TEMPLATE_PATHS.CONSOLE_LOGIN, values))
    
  def post(self):
    email = self.request.get("email")
    password = self.request.get("password")
    repeat_password = self.request.get('repeat_password')
    show_links = self.request.get("show_links")
    if not utils.validEmail(email):
      values = {"success" : False,
                "message" : "ERROR: You need to provide a valid email address."}
      if show_links == "yes":
        values['givelinks'] = True 
      self.response.out.write(template.render(constants.TEMPLATE_PATHS.CONSOLE_SIGN_UP, values))
      logging.error("Bad email %s"%email)
      return
    if password != repeat_password:
      values = {"success" : False,
                "message" : "ERROR: Passwords did not match."}
      if show_links == "yes":
        values['givelinks'] = True 
      logging.error("Bad passwords for email %s"%email)
      self.response.out.write(template.render(constants.TEMPLATE_PATHS.CONSOLE_SIGN_UP, values))
      return   
    ent_type = 'Accounts'
    existing_account = memcache_db.get_entity(email, ent_type)
    if existing_account != None:
      logging.error('An account already exists with that email: ' + existing_account.email)
 
      """ if the account is a test account, activate the account """
      if email in constants.TEST_ACCOUNTS and environment.is_dev():
        logging.debug("Account is a valid test account")
        
        memcache_db.delete_entity(existing_account, email)
        accounts_dao.create_account(email, password, True)
        
        message = "Your test account has been activated!"
        values = {"success" : True,
                "message" : message}
        if show_links == "yes":
          values['givelinks'] = True 
      elif existing_account.isEnabled == ACCOUNT_STATUS.PENDING_CREATE:
        """ REPEAT SIGN UP WITH UNACTIVATED ACCOUNT!!!!!!!!! """
        """ send the email again with the same activation ID """
        pc = pending_create_dao.get_id_by_email(email)
        activate_url = get_activate_url(pc.id)
        email_sent = send_email(email, activate_url)
        logging.info("Repeat sign up for account that was not activated yet. An email will be sent to with same activation link. Email: " + email + ", activation link: " + activate_url)
        message = ""
        if email_sent:
          message = "An email has been sent to you with a link to activate your account!"
        else:
          message = "There was an error during account creation. Please send an email to support@cloudcaptive.com"
        values = {"success" : True,
                  "message" : message}
        if show_links == "yes":
          values['givelinks'] = True 
        
      else:
        message = "ERROR: An account using this email address already exists. Contact support@cloudcaptive for support."
        values = {"success" : False,
                "message" : message}
        if show_links == "yes":
          values['givelinks'] = True 
    else:    
      """create an account and send an email for validation"""
      accounts_dao.create_account(email, password)
      
      """Add email to pending creates table"""
      id = str(uuid.uuid4())
      pending_create = Pending_Create(key_name=id, id=id, email=email)
      pending_create.put()
          
      
      """send an email to user to complete set up, get arguments in the string will be email and cookie ID"""
      activate_url = get_activate_url(id)
      logging.info("Activation URL for account: " + email + " is " + activate_url)
      email_sent = send_email(email, activate_url)
  
      message = ""
      if email_sent:
        message = "Sign up was a success. An activation link has been sent to your email address."
      else:
        message = "There was an error during account creation. Please send an email to support@cloudcaptive.com"
      values = {"success" : True,
                "message" : message}
      if show_links == "yes":
        values['givelinks'] = True 
    """ Render result with whatever values were filled in above """  
    self.response.out.write(template.render(constants.TEMPLATE_PATHS.CONSOLE_SIGN_UP, values))
      
def get_activate_url(id):
  return constants.WEB_SIGNUP_URLS.ACTIVATE_URL + "?activate=" + id

def send_email(email, activate_url):
  email_sent = False
  try:  
    mail.send_mail(sender="UserInfuser <" + constants.APP_OWNER_EMAIL + ">",
                   to=email,
                   subject="Welcome to UserInfuser!",
                   body= messages.get_activation_email(activate_url))
    email_sent = True
  except:
    email_sent = False
    logging.error("Error sending account activation email to account: " + email + ", activation url was: " + activate_url)
  return email_sent
