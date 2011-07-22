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
""" Author: Navraj Chohan
    Description: Information about the way a widget should be rendered
"""
from google.appengine.ext import db
from serverside import constants
""" Class: TrophyCase
    Description: Settings for rendering TrophyCase
"""
class TrophyCase(db.Model):
  backgroundColor = db.StringProperty( default="#eeeeff")
  borderThickness = db.IntegerProperty( default=1)
  borderColor = db.StringProperty( default="#4488FF")
  borderStyle = db.StringProperty( default="solid")
  height = db.IntegerProperty( default=500)
  width = db.IntegerProperty( default=270)
  hasRoundedCorners = db.BooleanProperty(default=False)
  # Title
  titleBackgroundColor = db.StringProperty(default="#4488FF")
  displayTitle = db.BooleanProperty( default=True)
  title = db.StringProperty( default="Trophy Case")
  titleColor = db.StringProperty( default="white")
  titleSize = db.IntegerProperty( default=20)
  titleFont = db.StringProperty( default="Arial")
  titleFloat = db.StringProperty( default="center")
  # Date
  displayDate = db.BooleanProperty( default=True)
  dateColor = db.StringProperty( default="black")
  dateSize = db.IntegerProperty( default=8)
  dateFont = db.StringProperty( default="Arial")
  dateFloat = db.StringProperty( default="center")
  # Reason for getting badge
  displayReason = db.BooleanProperty( default=True)
  reasonColor = db.StringProperty( default="black")
  reasonSize = db.IntegerProperty( default=12)
  reasonFont = db.StringProperty( default="Arial")
  reasonFloat = db.StringProperty( default="center")

  # Random/Misc
  allowSorting = db.BooleanProperty( default=True)
  imageSize = db.IntegerProperty( default=100) 
  scrollable = db.BooleanProperty( default=False)

  # what to display if there is an empty case
  displayNoBadgesMessage = db.BooleanProperty( default=True)
  noBadgesMessage = db.StringProperty( default="Sorry, no badges yet!")
  noBadgesFont = db.StringProperty( default="Arial")
  noBadgesSize = db.IntegerProperty( default=12)
  noBadgesFloat = db.StringProperty( default="center")
  noBadgesColor = db.StringProperty( default="red")

class Notifier(db.Model):
  backgroundColor = db.StringProperty(default="#EEEEFF")
  borderThickness = db.IntegerProperty(default=1)
  borderColor = db.StringProperty( default="#4488FF")
  borderStyle = db.StringProperty( default="solid")
  height = db.IntegerProperty(default=160)
  width = db.IntegerProperty(default=150)
  hasRoundedCorners = db.BooleanProperty(default=False)
  # Title
  titleBackgroundColor = db.StringProperty(default="#4488FF")
  displayTitle = db.BooleanProperty( default=True)
  title = db.StringProperty( default="Congrats!")
  titleColor = db.StringProperty( default="white")
  titleSize = db.IntegerProperty( default=10)
  titleFont = db.StringProperty( default="Arial")
  titleFloat = db.StringProperty( default="center")

  """http://docs.jquery.com/UI/Effects for different types""" 
  """'blind', 'clip', 'drop', 'explode', 'fold', 'puff', 'slide', 'scale', 'size', 'pulsate'."""
  exitEffect = db.StringProperty(default="fold")
  """'blind', 'clip', 'drop', 'explode', 'fold', 'puff', 'slide', 'scale', 'size', 'pulsate'."""
  entryEffect = db.StringProperty(default="drop")
  imageSize = db.IntegerProperty(default=100)

  # Note
  noteColor = db.StringProperty(default="#4488FF")
  displayNote = db.BooleanProperty( default=True)
  noteColor = db.StringProperty( default="#4488FF")
  noteSize = db.IntegerProperty( default=14)
  noteFont = db.StringProperty( default="Arial")
  noteFloat = db.StringProperty( default="center")

class Leaderboard(db.Model):
  backgroundColor = db.StringProperty( default="#EEEEFF")
  alternateColor = db.StringProperty( default="#DDFFFF")
  borderThickness = db.IntegerProperty( default=1)
  borderColor = db.StringProperty( default="#4488FF")
  borderStyle = db.StringProperty( default="solid")
  height = db.IntegerProperty( default=1000)
  width = db.IntegerProperty( default=500)
  hasRoundedCorners = db.BooleanProperty(default=False)
  imageSize = db.IntegerProperty(default=constants.IMAGE_PARAMS.LEADER_SIZE)

  # Title
  titleBackgroundColor = db.StringProperty(default="#4488FF")
  displayTitle = db.BooleanProperty( default=True)
  title = db.StringProperty( default="Leaderboard")
  titleColor = db.StringProperty( default="white")
  titleSize = db.IntegerProperty( default=20)
  titleFont = db.StringProperty( default="Arial")
  titleFloat = db.StringProperty( default="center")

  # Header
  headerBackgroundColor = db.StringProperty(default="#EEEEFF")
  displayHeader = db.BooleanProperty( default=True)
  headerColor = db.StringProperty( default="black")
  headerSize = db.IntegerProperty( default=20)
  headerFont = db.StringProperty( default="Arial")

  #Rank 
  rankColor = db.StringProperty(default="#4488FF")
  displayRank = db.BooleanProperty( default=True)
  rankColor = db.StringProperty( default="black")
  rankSize = db.IntegerProperty( default=25)
  rankFont = db.StringProperty( default="Arial")

  #Name 
  nameColor = db.StringProperty(default="#4488FF")
  displayName = db.BooleanProperty( default=True)
  nameColor = db.StringProperty( default="#4488FF")
  nameSize = db.IntegerProperty( default=14)
  nameFont = db.StringProperty( default="Arial")

  # Points
  pointsColor = db.StringProperty(default="#4488FF")
  displayPoints = db.BooleanProperty( default=True)
  pointsColor = db.StringProperty( default="#4488FF")
  pointsSize = db.IntegerProperty( default=20)
  pointsFont = db.StringProperty( default="Arial")
  pointsFloat = db.StringProperty( default="center")

  # what to display if there is an empty case
  displayNoUserMessage = db.BooleanProperty( default=True)
  noUserMessage = db.StringProperty( default="Check Back Soon!")
  noUserFont = db.StringProperty( default="Arial")
  noUserSize = db.IntegerProperty( default=20)
  noUserFloat = db.StringProperty( default="center")
  noUserColor = db.StringProperty( default="#FFF000")

class Points(db.Model):
  backgroundColor = db.StringProperty( default="#EEEEFF")
  borderThickness = db.IntegerProperty( default=1)
  borderColor = db.StringProperty( default="#4488FF")
  borderStyle = db.StringProperty( default="solid")
  height = db.IntegerProperty( default=100)
  width = db.IntegerProperty( default=120)
  hasRoundedCorners = db.BooleanProperty(default=False)
  # Title
  titleBackgroundColor = db.StringProperty(default="#4488FF")
  displayTitle = db.BooleanProperty( default=True)
  title = db.StringProperty( default="Your Points")
  titleColor = db.StringProperty( default="white")
  titleSize = db.IntegerProperty( default=14)
  titleFont = db.StringProperty( default="Arial")
  titleFloat = db.StringProperty( default="center")

  #displayPoints = db.BooleanProperty( default=True)
  pointsColor = db.StringProperty( default="black")
  pointsSize = db.IntegerProperty( default=14)
  pointsFont = db.StringProperty( default="Arial")
  pointsFloat = db.StringProperty( default="center")

class Rank(db.Model):
  backgroundColor = db.StringProperty( default="#EEEEFF")
  borderThickness = db.IntegerProperty( default=1)
  borderColor = db.StringProperty( default="#4488FF")
  borderStyle = db.StringProperty( default="solid")
  height = db.IntegerProperty( default=100)
  width = db.IntegerProperty( default=120)
  hasRoundedCorners = db.BooleanProperty(default=False)
  # Title
  displayTitle = db.BooleanProperty( default=True)
  title = db.StringProperty( default="Your Ranking")
  titleBackgroundColor = db.StringProperty(default="#4488FF")
  titleColor = db.StringProperty( default="white")
  titleSize = db.IntegerProperty( default=14)
  titleFont = db.StringProperty( default="Arial")
  titleFloat = db.StringProperty( default="center")
  # Rank
  rankColor = db.StringProperty( default="black")
  rankSize = db.IntegerProperty( default=14)
  rankFont = db.StringProperty( default="Arial")
  rankFloat = db.StringProperty( default="center")

class Milestones(db.Model):
  backgroundColor = db.StringProperty( default="#eeeeff")
  borderThickness = db.IntegerProperty( default=1)
  borderColor = db.StringProperty( default="#4488FF")
  borderStyle = db.StringProperty( default="solid")
  height = db.IntegerProperty( default=500)
  width = db.IntegerProperty( default=270)
  hasRoundedCorners = db.BooleanProperty(default=False)
  # Title
  titleBackgroundColor = db.StringProperty(default="#4488FF")
  displayTitle = db.BooleanProperty( default=True)
  title = db.StringProperty( default="Badge Progress")
  titleColor = db.StringProperty( default="white")
  titleSize = db.IntegerProperty( default=20)
  titleFont = db.StringProperty( default="Arial")
  titleFloat = db.StringProperty( default="center")
  # Date
  displayDate = db.BooleanProperty( default=True)
  dateColor = db.StringProperty( default="black")
  dateSize = db.IntegerProperty( default=8)
  dateFont = db.StringProperty( default="Arial")
  dateFloat = db.StringProperty( default="center")
  # Reason for getting badge
  displayReason = db.BooleanProperty( default=True)
  reasonColor = db.StringProperty( default="black")
  reasonSize = db.IntegerProperty( default=12)
  reasonFont = db.StringProperty( default="Arial")
  reasonFloat = db.StringProperty( default="center")

  # Random/Misc
  allowSorting = db.BooleanProperty( default=True)
  imageSize = db.IntegerProperty( default=100) 
  scrollable = db.BooleanProperty( default=False)


