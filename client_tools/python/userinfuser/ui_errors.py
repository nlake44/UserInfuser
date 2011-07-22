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

class Error(Exception):
  """ Base Error Type """

class InternalError(Error):
  """ Internal error within API """

class BadgeDoesNotExist(Error):
  """ The given badge id does not exist """

class UserDoesNotExist(Error):
  """ The given user id does not exist """

class ConnectionError(Error):
  """ Unable to make a connection to UI service """

class BadConfiguration(Error):
  """ Unable to find API key """

class PermissionDenied(Error):
  """ Check your api key or your account email """

class UnknownWidget(Error):
  """ Check valid widgets for the correct type """

class BadArgument(Error):
  """ Check your arguments and try again """

ui_error_map = {1: PermissionDenied,
                2: BadgeDoesNotExist,
                3: UserDoesNotExist,
                4: InternalError,
                5: BadArgument}
