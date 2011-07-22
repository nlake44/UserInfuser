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

class TestGetWidget < Test::Unit::TestCase
  def test_user_good
    [SYNC_ALL, ASYNC_ALL].each { |sync|
      update_user_good(sync)
    }
  end

  def update_user_good(sync)
    ui = get_good_ui(sync)

    ["trophy_case", "milestones", "points", "rank", "notifier"].each { |item|
      puts ui.get_widget(ID1, item)
      assert(ui.get_widget(ID1, item).to_s.include?(item))
    }

    assert_raise(UserInfuserUnknownWidget) { ui.get_widget(ID1, "doesnotexist") }
  end
end

