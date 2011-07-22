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

class TestAwardBadges < Test::Unit::TestCase
  def test_award_sync_good
    ui = get_good_ui(SYNC_ALL)

    assert(ui.award_badge(ID1, BADGEID1, REASON))
    assert_equal(false, ui.award_badge(ID1, "", REASON))
    assert_equal(false, ui.award_badge(ID1, BADGEID1 + "xxx", REASON))
    assert(ui.award_badge(ID1, BADGEID2, REASON))

    assert(ui.remove_badge(ID1, BADGEID3))
    assert_equal(false, ui.get_user_data(ID1).to_s.include?(BADGEID3))

    assert(ui.award_badge_points(ID1, BADGEID3, 10, 100, REASON))
    assert(ui.award_badge_points(ID1, BADGEID3, 10, 100, REASON))
    assert(ui.award_badge_points(ID1, BADGEID3, 10, 100, REASON))
    assert_equal(false, ui.get_user_data(ID1).to_s.include?(BADGEID3))
    
    assert(ui.award_badge_points(ID1, BADGEID3, 70, 100, REASON))
    assert(ui.get_user_data(ID1).to_s.include?(BADGEID3))
  end

  def test_award_sync_bad
    ui = get_bad_ui(SYNC_ALL)

    assert_equal(false, ui.award_badge(ID1, BADGEID1, REASON))
    assert_equal(false, ui.award_badge(ID1, BADGEID2, REASON))
  end

  def test_award_async_good
    ui = get_good_ui(ASYNC_ALL)

    assert(ui.award_badge(ID1, BADGEID1, REASON))
    assert(ui.award_badge(ID1, "", REASON))
    assert(ui.award_badge(ID1, BADGEID1 + "xxx", REASON))
    assert(ui.award_badge(ID1, BADGEID2, REASON))

    assert(ui.remove_badge(ID1, BADGEID3))
    sleep(1)
    assert_equal(false, ui.get_user_data(ID1).to_s.include?(BADGEID3))

    3.times {
      assert(ui.award_badge_points(ID1, BADGEID3, 10, 100, REASON))
      sleep(1)
    }

    assert_equal(false, ui.get_user_data(ID1).to_s.include?(BADGEID3))

    3.times {
      assert(ui.award_badge_points(ID1, BADGEID3, 70, 100, REASON))
    }

    sleep(2)
    assert(ui.get_user_data(ID1).to_s.include?(BADGEID3))
  end

  def test_award_async_bad
    ui = get_good_ui(ASYNC_ALL)

    assert(ui.award_badge(ID1, BADGEID1, REASON))
    assert(ui.award_badge(ID1, BADGEID2, REASON))
  end
end

