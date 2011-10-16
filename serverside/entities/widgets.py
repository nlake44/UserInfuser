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
  backgroundColor = db.StringProperty( default="#eeeeff", indexed=False)
  borderThickness = db.IntegerProperty( default=1, indexed=False)
  borderColor = db.StringProperty( default="#4488FF", indexed=False)
  borderStyle = db.StringProperty( default="solid", indexed=False)
  height = db.IntegerProperty( default=500, indexed=False)
  width = db.IntegerProperty( default=270, indexed=False)
  hasRoundedCorners = db.BooleanProperty(default=False, indexed=False)
  # Title
  titleBackgroundColor = db.StringProperty(default="#4488FF", indexed=False)
  displayTitle = db.BooleanProperty( default=True, indexed=False)
  title = db.StringProperty( default="Trophy Case", indexed=False)
  titleColor = db.StringProperty( default="white", indexed=False)
  titleSize = db.IntegerProperty( default=20, indexed=False)
  titleFont = db.StringProperty( default="Arial", indexed=False)
  titleFloat = db.StringProperty( default="center", indexed=False)
  # Date
  displayDate = db.BooleanProperty( default=True, indexed=False)
  dateColor = db.StringProperty( default="black", indexed=False)
  dateSize = db.IntegerProperty( default=8, indexed=False)
  dateFont = db.StringProperty( default="Arial", indexed=False)
  dateFloat = db.StringProperty( default="center", indexed=False)
  # Reason for getting badge
  displayReason = db.BooleanProperty( default=True, indexed=False)
  reasonColor = db.StringProperty( default="black", indexed=False)
  reasonSize = db.IntegerProperty( default=12, indexed=False)
  reasonFont = db.StringProperty( default="Arial", indexed=False)
  reasonFloat = db.StringProperty( default="center", indexed=False)

  # Random/Misc
  allowSorting = db.BooleanProperty( default=True, indexed=False)
  imageSize = db.IntegerProperty( default=100, indexed=False) 
  scrollable = db.BooleanProperty( default=False, indexed=False)

  # what to display if there is an empty case
  displayNoBadgesMessage = db.BooleanProperty( default=True, indexed=False)
  noBadgesMessage = db.StringProperty( default="Sorry, no badges yet!", indexed=False)
  noBadgesFont = db.StringProperty( default="Arial", indexed=False)
  noBadgesSize = db.IntegerProperty( default=12, indexed=False)
  noBadgesFloat = db.StringProperty( default="center", indexed=False)
  noBadgesColor = db.StringProperty( default="red", indexed=False)

class Notifier(db.Model):
  backgroundColor = db.StringProperty(default="#EEEEFF", indexed=False)
  borderThickness = db.IntegerProperty(default=1, indexed=False)
  borderColor = db.StringProperty( default="#4488FF", indexed=False)
  borderStyle = db.StringProperty( default="solid", indexed=False)
  height = db.IntegerProperty(default=160, indexed=False)
  width = db.IntegerProperty(default=150, indexed=False)
  hasRoundedCorners = db.BooleanProperty(default=False, indexed=False)
  # Title
  titleBackgroundColor = db.StringProperty(default="#4488FF", indexed=False)
  displayTitle = db.BooleanProperty( default=True, indexed=False)
  title = db.StringProperty( default="Congrats!", indexed=False)
  titleColor = db.StringProperty( default="white", indexed=False)
  titleSize = db.IntegerProperty( default=10, indexed=False)
  titleFont = db.StringProperty( default="Arial", indexed=False)
  titleFloat = db.StringProperty( default="center", indexed=False)

  """http://docs.jquery.com/UI/Effects for different types""" 
  """'blind', 'clip', 'drop', 'explode', 'fold', 'puff', 'slide', 'scale', 'size', 'pulsate'."""
  exitEffect = db.StringProperty(default="fold", indexed=False)
  """'blind', 'clip', 'drop', 'explode', 'fold', 'puff', 'slide', 'scale', 'size', 'pulsate'."""
  entryEffect = db.StringProperty(default="drop", indexed=False)
  imageSize = db.IntegerProperty(default=100, indexed=False)

  # Note
  noteColor = db.StringProperty(default="#4488FF", indexed=False)
  displayNote = db.BooleanProperty( default=True, indexed=False)
  noteColor = db.StringProperty( default="#4488FF", indexed=False)
  noteSize = db.IntegerProperty( default=14, indexed=False)
  noteFont = db.StringProperty( default="Arial", indexed=False)
  noteFloat = db.StringProperty( default="center", indexed=False)

class Leaderboard(db.Model):
  backgroundColor = db.StringProperty( default="#EEEEFF", indexed=False)
  alternateColor = db.StringProperty( default="#DDFFFF", indexed=False)
  borderThickness = db.IntegerProperty( default=1, indexed=False)
  borderColor = db.StringProperty( default="#4488FF", indexed=False)
  borderStyle = db.StringProperty( default="solid", indexed=False)
  height = db.IntegerProperty( default=1000, indexed=False)
  width = db.IntegerProperty( default=500, indexed=False)
  hasRoundedCorners = db.BooleanProperty(default=False, indexed=False)
  imageSize = db.IntegerProperty(default=constants.IMAGE_PARAMS.LEADER_SIZE, indexed=False)

  # Title
  titleBackgroundColor = db.StringProperty(default="#4488FF", indexed=False)
  displayTitle = db.BooleanProperty( default=True, indexed=False)
  title = db.StringProperty( default="Leaderboard", indexed=False)
  titleColor = db.StringProperty( default="white", indexed=False)
  titleSize = db.IntegerProperty( default=20, indexed=False)
  titleFont = db.StringProperty( default="Arial", indexed=False)
  titleFloat = db.StringProperty( default="center", indexed=False)

  # Header
  headerBackgroundColor = db.StringProperty(default="#EEEEFF", indexed=False)
  displayHeader = db.BooleanProperty( default=True, indexed=False)
  headerColor = db.StringProperty( default="black", indexed=False)
  headerSize = db.IntegerProperty( default=20, indexed=False)
  headerFont = db.StringProperty( default="Arial", indexed=False)

  #Rank 
  rankColor = db.StringProperty(default="#4488FF", indexed=False)
  displayRank = db.BooleanProperty( default=True, indexed=False)
  rankColor = db.StringProperty( default="black", indexed=False)
  rankSize = db.IntegerProperty( default=25, indexed=False)
  rankFont = db.StringProperty( default="Arial", indexed=False)

  #Name 
  nameColor = db.StringProperty(default="#4488FF", indexed=False)
  displayName = db.BooleanProperty( default=True, indexed=False)
  nameColor = db.StringProperty( default="#4488FF", indexed=False)
  nameSize = db.IntegerProperty( default=14, indexed=False)
  nameFont = db.StringProperty( default="Arial", indexed=False)

  # Points
  pointsColor = db.StringProperty(default="#4488FF", indexed=False)
  displayPoints = db.BooleanProperty( default=True, indexed=False)
  pointsColor = db.StringProperty( default="#4488FF", indexed=False)
  pointsSize = db.IntegerProperty( default=20, indexed=False)
  pointsFont = db.StringProperty( default="Arial", indexed=False)
  pointsFloat = db.StringProperty( default="center", indexed=False)

  # what to display if there is an empty case
  displayNoUserMessage = db.BooleanProperty( default=True, indexed=False)
  noUserMessage = db.StringProperty( default="Check Back Soon!", indexed=False)
  noUserFont = db.StringProperty( default="Arial", indexed=False)
  noUserSize = db.IntegerProperty( default=20, indexed=False)
  noUserFloat = db.StringProperty( default="center", indexed=False)
  noUserColor = db.StringProperty( default="#FFF000", indexed=False)

class Points(db.Model):
  backgroundColor = db.StringProperty( default="#EEEEFF", indexed=False)
  borderThickness = db.IntegerProperty( default=1, indexed=False)
  borderColor = db.StringProperty( default="#4488FF", indexed=False)
  borderStyle = db.StringProperty( default="solid", indexed=False)
  height = db.IntegerProperty( default=100, indexed=False)
  width = db.IntegerProperty( default=120, indexed=False)
  hasRoundedCorners = db.BooleanProperty(default=False, indexed=False)
  # Title
  titleBackgroundColor = db.StringProperty(default="#4488FF", indexed=False)
  displayTitle = db.BooleanProperty( default=True, indexed=False)
  title = db.StringProperty( default="Your Points", indexed=False)
  titleColor = db.StringProperty( default="white", indexed=False)
  titleSize = db.IntegerProperty( default=14, indexed=False)
  titleFont = db.StringProperty( default="Arial", indexed=False)
  titleFloat = db.StringProperty( default="center", indexed=False)

  #displayPoints = db.BooleanProperty( default=True)
  pointsColor = db.StringProperty( default="black", indexed=False)
  pointsSize = db.IntegerProperty( default=14, indexed=False)
  pointsFont = db.StringProperty( default="Arial", indexed=False)
  pointsFloat = db.StringProperty( default="center", indexed=False)

class Rank(db.Model):
  backgroundColor = db.StringProperty( default="#EEEEFF", indexed=False)
  borderThickness = db.IntegerProperty( default=1, indexed=False)
  borderColor = db.StringProperty( default="#4488FF", indexed=False)
  borderStyle = db.StringProperty( default="solid", indexed=False)
  height = db.IntegerProperty( default=100, indexed=False)
  width = db.IntegerProperty( default=120, indexed=False)
  hasRoundedCorners = db.BooleanProperty(default=False, indexed=False)
  # Title
  displayTitle = db.BooleanProperty( default=True, indexed=False)
  title = db.StringProperty( default="Your Ranking", indexed=False)
  titleBackgroundColor = db.StringProperty(default="#4488FF", indexed=False)
  titleColor = db.StringProperty( default="white", indexed=False)
  titleSize = db.IntegerProperty( default=14, indexed=False)
  titleFont = db.StringProperty( default="Arial", indexed=False)
  titleFloat = db.StringProperty( default="center", indexed=False)
  # Rank
  rankColor = db.StringProperty( default="black", indexed=False)
  rankSize = db.IntegerProperty( default=14, indexed=False)
  rankFont = db.StringProperty( default="Arial", indexed=False)
  rankFloat = db.StringProperty( default="center", indexed=False)

class Milestones(db.Model):
  backgroundColor = db.StringProperty( default="#eeeeff", indexed=False)
  borderThickness = db.IntegerProperty( default=1, indexed=False)
  borderColor = db.StringProperty( default="#4488FF", indexed=False)
  borderStyle = db.StringProperty( default="solid", indexed=False)
  height = db.IntegerProperty( default=500, indexed=False)
  width = db.IntegerProperty( default=270, indexed=False)
  hasRoundedCorners = db.BooleanProperty(default=False, indexed=False)
  # Title
  titleBackgroundColor = db.StringProperty(default="#4488FF", indexed=False)
  displayTitle = db.BooleanProperty( default=True, indexed=False)
  title = db.StringProperty( default="Badge Progress", indexed=False)
  titleColor = db.StringProperty( default="white", indexed=False)
  titleSize = db.IntegerProperty( default=20, indexed=False)
  titleFont = db.StringProperty( default="Arial", indexed=False)
  titleFloat = db.StringProperty( default="center", indexed=False)
  # Date
  displayDate = db.BooleanProperty( default=True, indexed=False)
  dateColor = db.StringProperty( default="black", indexed=False)
  dateSize = db.IntegerProperty( default=8, indexed=False)
  dateFont = db.StringProperty( default="Arial", indexed=False)
  dateFloat = db.StringProperty( default="center", indexed=False)
  # Reason for getting badge
  displayReason = db.BooleanProperty( default=True, indexed=False)
  reasonColor = db.StringProperty( default="black", indexed=False)
  reasonSize = db.IntegerProperty( default=12, indexed=False)
  reasonFont = db.StringProperty( default="Arial", indexed=False)
  reasonFloat = db.StringProperty( default="center", indexed=False)

  # Random/Misc
  allowSorting = db.BooleanProperty( default=True, indexed=False)
  imageSize = db.IntegerProperty( default=100, indexed=False) 
  scrollable = db.BooleanProperty( default=False, indexed=False)


