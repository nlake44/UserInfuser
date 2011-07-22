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
Created on Jan 9, 2011

@author: shan

This class shall hold messages that the server will be using for standard use, for example, email notifications.
'''


def get_activation_email(activation_url):
  """Get email message that goes out to customers when the sign up, for activation.
  
  activation_url is the url that will process the activation request. It will be embeded
  into the message.
  
  """
  
  message ="""  
Hello,
                      
Thank you for signing up for UserInfuser. Please click the following link to activate your account:
                      
""" + activation_url + """
                      
Thank you!
"""
  return message 



def get_forgotten_login_email(new_password):
  """
  Message formatted with a new password for forgotten login queries
  """
  
  message = """

You account password has been reset to the following: """ + new_password + """

Please login and change your password.

Thank you,

UserInfuser Team.
  
"""
  return message  
