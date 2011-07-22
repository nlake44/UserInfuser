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
#             Navraj Chohan

require 'rubygems'
require 'json'

require 'digest/sha1'
require 'logger'
require 'net/http'
require 'uri'

class UserInfuserBadConfiguration < StandardError
end

class UserInfuserUnknownWidget < StandardError
end

class UserInfuser
  UI_SPATH = "https://cloudcaptive-userinfuser.appspot.com/api/"
  UI_PATH = "http://cloudcaptive-userinfuser.appspot.com/api/"
  LOCAL_TEST = "http://localhost:8080/api/"
  API_VER = "1"
  VALID_WIDGETS = ["trophy_case", "milestones", "notifier", "points", "rank", "availablebadges", "leaderboard"]
  UPDATE_USER_PATH = "updateuser"
  GET_USER_DATA_PATH = "getuserdata"
  AWARD_BADGE_PATH = "awardbadge"
  REMOVE_BADGE_PATH = "removebadge"
  AWARD_BADGE_POINTS_PATH = "awardbadgepoints"
  AWARD_POINTS_PATH = "awardpoints"
  WIDGET_PATH = "getwidget"
  CREATE_BADGE_PATH= "createbadge"
  RAISE_EXCEPTIONS = false
  UI_ANONYMOUS = "__ui__anonymous__"

  def initialize(account, api_key, debug=false, local=false, encrypt=true, sync_all=false)
    @ui_url = UI_PATH
    @ui_url = UI_SPATH if encrypt

    @isGAE = false
    @sync_all = sync_all

    @debug = debug
    log_debug "debug is on, account: #{account}, apikey: #{api_key}"

    @api_key = api_key
    raise UserInfuserBadConfiguration if account.nil? or api_key.nil?

    @account = account

    @raise_exceptions = RAISE_EXCEPTIONS

    if local
      @ui_url = LOCAL_TEST
      log_debug "Local testing enabled"
      @raise_exceptions = true
    end

    @update_user_path = @ui_url + API_VER + "/" + UPDATE_USER_PATH
    @award_badge_path = @ui_url + API_VER + "/" + AWARD_BADGE_PATH
    @award_badge_points_path = @ui_url + API_VER + "/"+ AWARD_BADGE_POINTS_PATH
    @award_points_path = @ui_url + API_VER + "/"+ AWARD_POINTS_PATH
    @get_user_data_path = @ui_url + API_VER + "/" + GET_USER_DATA_PATH
    @remove_badge_path = @ui_url + API_VER + "/" + REMOVE_BADGE_PATH
    @widget_path = @ui_url + API_VER + "/" + WIDGET_PATH
    @create_badge_path = @ui_url + API_VER + "/" + CREATE_BADGE_PATH

    @timeout = 10 # seconds
  end

  def get_user_data(id)
    params = { "apikey" => @api_key,
               "userid" => id,
               "accountid" => @account
             }

    result = '{"status":"failed"}'

    begin
      result = post(@get_user_data_path, params)
      log_debug "Received #{result}"
    rescue Exception => e
      log_debug "Connection Error"
      raise e if @raise_exceptions
    end

    begin
      result = JSON.parse(result)
    rescue
      log_debug "Unable to parse return message"
    end

    return result
  end

  def update_user(id, name, link_to_profile, link_to_profile_image)
    params = { "apikey" => @api_key,
               "userid" => id,
               "accountid" => @account,
               "profile_name" => name,
               "profile_link" => link_to_profile,
               "profile_img" => link_to_profile_image
             }

    if @sync_all
      result = post(@update_user_path, params)
      return parse_return(result)
    else
      async_post(@update_user_path, params)
      return true
    end
  end

  def award_badge(user_id, badge_id, reason="", resource="")
    params = { "apikey" => @api_key,
               "accountid" => @account,
               "userid" => user_id,
               "badgeid" => badge_id,
               "resource" => resource,
               "reason" => reason}

    result = nil
    begin
      if @sync_all
        result = post(@award_badge_path, params)
      else
        async_post(@award_badge_path, params)
        return true
      end

      log_debug "Received: #{result}"
    rescue Exception => e
      log_debug "Connection Error"
      raise e if @raise_exceptions
    end

    return parse_return(result)
  end

  def remove_badge(user_id, badge_id)
    params = {"apikey" => @api_key,
               "accountid" => @account,
               "userid" => user_id,
               "badgeid" => badge_id
             }

    result = nil
    begin
      if @sync_all
        result = post(@remove_badge_path, params)
      else
        async_post(@remove_badge_path, params)
        return true
      end

      log_debug "Received: #{result}"
    rescue Exception => e
      log_debug "Connection Error"
      raise e if @raise_exceptions
    end

    return parse_return(result)
  end

  def award_points(user_id, points_awarded, reason="")
    params = { "apikey" => @api_key,
               "accountid" => @account,
               "userid" => user_id,
               "pointsawarded" => points_awarded,
               "reason" => reason
             }

    result = nil
    begin
      if @sync_all
        result = post(@award_points_path, params)
      else
        async_post(@award_points_path, params)
        return true
      end

      log_debug "Received #{result}" 
    rescue Exception => e
      log_debug "Connection Error"
      raise e if @raise_exceptions
    end

    return parse_return(result)
  end

  def award_badge_points(user_id, badge_id, points_awarded, points_required, reason="", resource="")
    params = { "apikey" => @api_key,
               "accountid" => @account,
               "userid" => user_id,
               "badgeid" => badge_id,
               "pointsawarded" => points_awarded,
               "pointsrequired" => points_required,
               "reason" => reason,
               "resource" => resource}

    result = nil
    begin
      if @sync_all
        result = post(@award_badge_points_path, params)
      else
        async_post(@award_badge_points_path, params)
        return true
      end

      log_debug "Received: #{result}"
    rescue Exception => e
      log_debug "Connection Error" 
      raise e if @raise_exceptions
    end

    return parse_return(result)
  end

  def get_widget(user_id, widget_type, height=500, width=300)
    raise UserInfuserUnknownWidget unless VALID_WIDGETS.include?(widget_type)
    
    user_id = UI_ANONYMOUS if user_id.nil?
    user_id = UI_ANONYMOUS if user_id.empty?
     
    userhash = Digest::SHA1.hexdigest(@account + '---' + user_id)
    prefetch_widget(widget_type, user_id)
    if widget_type == "notifier"
      return "<div style='z-index:9999; overflow: hidden; position: fixed; bottom: 0px; right: 10px;'><iframe style='border:none;' allowtransparency='true' height='#{height}px' width='#{width}px' scrolling='no' src='#{@widget_path}?widget=#{widget_type}&u=#{userhash}&height=#{height}&width=#{width}'>Sorry your browser does not support iframes!</iframe></div>"
    else
      return "<iframe border='0' z-index:9999; frameborder='0' height='#{height}px' width='#{width}px' allowtransparency='true' scrolling='no' src='#{@widget_path}?widget=#{widget_type}&u=#{userhash}&height=#{height}&width=#{width}'>Sorry your browser does not support iframes!</iframe>"
    end
  end

  private

  def post(path, params)
    uri = URI.parse(path)
    response = Net::HTTP.post_form(uri, params)
    return response.body
  end

  def async_post(path, params)
    Thread.new { post(path, params) }
  end

  def parse_return(string)
    json = nil

    begin
      json = JSON.parse(string)
    rescue
      log_debug "unable to parse return message"
      return false
    end

    if json['status'] == 'failed'
      log_debug json['error']
      return false
    end

    return true
  end

  def prefetch_widget(widget_type, user_id)
    params = {"apikey" => @api_key,
               "accountid" => @account,
               "userid" => user_id,
               "widget" => widget_type
             }

    begin
      async_post(@widget_path, params)
    rescue
    end
  end

  def log_debug(msg)
    puts msg if @debug    
  end
end

