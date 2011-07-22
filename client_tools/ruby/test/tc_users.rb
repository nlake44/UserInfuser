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

class TestUsers < Test::Unit::TestCase
  def test_prime_db
    prime_success = TestHelper.post(PRIME_PATH, PARAMS)
    assert_equal(SUCCESS, prime_success)

    delete_success = TestHelper.post(DELETE_PATH, PARAMS)
    assert_equal(SUCCESS, delete_success)

    prime_success = TestHelper.post(PRIME_PATH, PARAMS)
    assert_equal(SUCCESS, prime_success)
  end

  def test_update_user_sync_good
    ui = get_good_ui(SYNC_ALL)

    user_name = "Raaaaaaj"
    user_url = "http://facebook.com/nlake44"
    user_img = "http://imgur.com/AK9Fw"

    assert(ui.update_user(ID1, user_name, user_url, user_img))

    user_name2 = "Raj"
    user_img2 = "http://profile.ak.fbcdn.net/hprofile-ak-snc4/203059_3610637_6604695_n.jpg"

    assert(ui.update_user(ID1, user_name2, user_url, user_img2))

    user_name3 = "Billy Gene"
    user_url3 = "http://www.facebook.com/isnotmylove"
    user_img3 = "http://cdn3.iconfinder.com/data/icons/faceavatars/PNG/J01.png"
    assert(ui.update_user(ID2, user_name3, user_url3, user_img3))
  end

  def test_update_user_sync_bad
    ui = get_bad_ui(SYNC_ALL)

    user_name = "Heather"
    user_url = "http://www.facebook.com/profile.php?id=710661131"
    user_img = "http://profile.ak.fbcdn.net/hprofile-ak-snc4/203293_710661131_7132437_n.jpg"

    assert_equal(false, ui.update_user(ID1, user_name, user_url, user_img))

    user_name2 = "Jack Smith"
    user_url2 = "http://test.com/a"
    user_img2 = "http://test.com/a/image"

    assert_equal(false, ui.update_user(ID1, user_name2, user_url2, user_img2))
  end

  def test_update_user_async_good
    ui = get_good_ui(ASYNC_ALL)

    user_name = "Raj"
    user_url = "http://facebook.com/nlake44"
    user_img = "http://imgur.com/AK9Fw"

    assert(ui.update_user(ID1, user_name, user_url, user_img))

    user_name2 = "Jakob"
    user_url2 = "http://profile.ak.fbcdn.net/hprofile-ak-snc4/49299_669633666_9641_n.jpg"
    user_img2 = "http://profile.ak.fbcdn.net/hprofile-ak-snc4/49299_669633666_9641_n.jpg"

    assert(ui.update_user(ID1, user_name2, user_url2, user_img2))

    user_name3 = "Shan"
    user_url3 = "http://www.facebook.com/profile.php?id=3627076"
    user_img3 = "http://www.facebook.com/album.php?profile=1&id=3627076"

    assert(ui.update_user(ID1, user_name3, user_url3, user_img3))
  end

  def test_update_user_async_bad
    ui = get_bad_ui(ASYNC_ALL)

    user_name = "a"
    user_url = "http://test.com/a"
    user_img = "http://test.com/a/image"
    
    assert(ui.update_user(ID1, user_name, user_url, user_img))

    user_name2 = "Jack Smith"
    user_url2 = "http://test.com/a"
    user_img2 = "http://test.com/a/image"

    assert(ui.update_user(ID1, user_name2, user_url2, user_img2))
  end
end

