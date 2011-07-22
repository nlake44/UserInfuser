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

class TestGetUserData < Test::Unit::TestCase
  def test_getuserdata_sync_good
    ui = get_good_ui(SYNC_ALL)

    assert(ui.get_user_data(ID1).to_s.include?(BADGEID1))
    assert(ui.get_user_data(ID1).to_s.include?(BADGEID2))
    assert(ui.get_user_data(ID1).to_s.include?(ID1))

    assert(ui.get_user_data(ID1).to_s.include?("200"))
    assert_equal("failed", ui.get_user_data("blahblahblah___"))

    if CLEANUP
      assert(ui.remove_badge(ID1, BADGEID1))
      assert(ui.remove_badge(ID1, BADGEID2))
      assert(ui.remove_badge(ID1, BADGEID3))
    end

    assert_equal(false, ui.remove_badge(ID1, "-x-x-x" + BADGEID3 + "xxx"))
  end

  def test_getuserdata_sync_bad
    ui = get_bad_ui(SYNC_ALL)

    assert(ui.get_user_data(ID1).to_s.include?("failed"))
  end

  def test_delete_path
    assert_equal(SUCCESS, TestHelper.post(DELETE_PATH, PARAMS))
  end

  def test_getuserdata_async_good
    ui = get_good_ui(ASYNC_ALL)

    sleep(1)
    [BADGEID1, BADGEID2, ID1, "200"].each { |item|
      assert(ui.get_user_data(ID1).to_s.include?(item))
    }

    if CLEANUP
      [BADGEID1, BADGEID2, BADGEID3].each { |badge|
        assert(ui.remove_badge(ID1, badge))
      }
    end

    assert(ui.remove_badge(TESTID, "-x-x-x" + BADGEID3 + "xxx"))

    user_name = "Raj"
    user_url = "http://www.facebook.com/nlake44"
    user_img="http://profile.ak.fbcdn.net/hprofile-ak-snc4/203059_3610637_6604695_n.jpg"
    assert(ui.update_user(ID2, user_name, user_url, user_img))

    r = "rank"
    assert(ui.get_widget(ID2, r).to_s.include?(r))

    assert(ui.award_points(ID2, 10))
    assert(ui.update_user(ID3))

    badge_img = "http://cdn1.iconfinder.com/data/icons/Futurosoft%20Icons%200.5.2/128x128/apps/limewire.png"
    assert(ui.create_badge("apple","oranges","fruit", badge_img))
    sleep(1)
  end

  def test_cleanup
    return unless CLEANUP

    params = {
      "apikey" => API_KEY,
      "accountid" => ACCOUNT,
      "badgeid" => BADGEID1,
      "secret" => SECRET,
      "user" => ID1,
      "theme" => BADGETHEME
    }

    [ID1, ID2, ID3].each { |id|
      params['user'] = id
      assert(TestHelper.post(PRIME_PATH, params).include?("success"))
      assert(TestHelper.post(DELETE_PATH, params).include?("success"))
    }
  end
end

