<?php
  /*
    Copyright (C) 2011, CloudCaptive

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
  */
  define('UI_CONSTANTS_PATH','http://cloudcaptive-userinfuser.appspot.com/api/');
  define('UI_CONSTANTS_SPATH', 'https://cloudcaptive-userinfuser.appspot.com/api/');
  define('UI_CONSTANTS_LOCAL_TEST','http://localhost:8080/api/');
  define('UI_CONSTANTS_API_VER','1');
  define('UI_CONSTANTS_UPDATE_USER_PATH', 'updateuser');
  define('UI_CONSTANTS_GET_USER_DATA_PATH','getuserdata');
  define('UI_CONSTANTS_AWARD_BADGE_PATH','awardbadge');
  define('UI_CONSTANTS_REMOVE_BADGE_PATH','removebadge');
  define('UI_CONSTANTS_AWARD_BADGE_POINTS_PATH','awardbadgepoints');
  define('UI_CONSTANTS_AWARD_POINTS_PATH','awardpoints');
  define('UI_CONSTANTS_WIDGET_PATH','getwidget');
  define('UI_CONSTANTS_TIMEOUT',10);
  define('UI_CONSTANTS_ANONYMOUS','__ui__anonymous__');
  /*****************************************
  * Class: UserInfuser
  * Parameters: 
  *             account: account email you registered with at the
  *                      UserInfuser site
  *             api_key: The key provided by UserInfuser
  * Exception: Tosses an exception if the curl library is not installed,
  *            or the account and/or api key are not provided
  * Notes: Check the website for which widgets are available.
  ****************************************/
  class UserInfuser
  {
    private $account, $ui_url, $debug, $api_key, $local;
    private $update_user_path, $award_badge_path, $award_badge_points_path;
    private $award_points_path, $get_user_data_path, $remove_badge_path;
    private $widget_path, $valid_widgets;
    public function __construct($account, $api_key)
    {
      if (!$account or !$api_key){
        throw new Exception('Bad configuration');
      }
      if (!$this->__ui_cURLcheckBasicFunctions()){
        throw new Exception('Please install cURL php libraries'); 
      }
      $this->account = ($account);
      $this->api_key = $api_key;
      $this->debug = False;
      $this->local = False;
      $this->only_sync = False;
      $this->ui_url = UI_CONSTANTS_PATH;
      $this->update_user_path = $this->ui_url . UI_CONSTANTS_API_VER . "/" .
                         UI_CONSTANTS_UPDATE_USER_PATH;
      $this->award_badge_path = $this->ui_url . UI_CONSTANTS_API_VER . "/" .
                         UI_CONSTANTS_AWARD_BADGE_PATH;
      $this->award_badge_points_path = $this->ui_url . UI_CONSTANTS_API_VER . 
                         "/". UI_CONSTANTS_AWARD_BADGE_POINTS_PATH;
      $this->award_points_path = $this->ui_url . UI_CONSTANTS_API_VER . "/" .
                         UI_CONSTANTS_AWARD_POINTS_PATH;
      $this->get_user_data_path = $this->ui_url . UI_CONSTANTS_API_VER . "/".
                         UI_CONSTANTS_GET_USER_DATA_PATH;
      $this->remove_badge_path = $this->ui_url . UI_CONSTANTS_API_VER . "/" .
                         UI_CONSTANTS_REMOVE_BADGE_PATH;
      $this->widget_path = $this->ui_url . UI_CONSTANTS_API_VER . "/" .
                         UI_CONSTANTS_WIDGET_PATH;
      $this->valid_widgets = array("trophy_case", "milestones", "notifier", "points", "leaderboard", "rank", "availablebadges", "leaderboard");
    }
    /*****************************************
    * Name: enable_debug
    * Description: Enables logging of debug info
    * Parameters: None
    * Returns: Nothing
    * Notes: None 
    ****************************************/
    public function enable_debug()
    {
      $this->debug = True;
      print "Debugging is enabled\n";
    }
    /*****************************************
    * Name: enable_encryption
    * Description: All calls will use HTTPS
    * Parameters: None 
    * Returns: Nothing
    * Notes: None
    ****************************************/
    public function enable_encryption()
    {
      $this->ui_url = UI_CONSTANTS_PATH;
      $this->update_user_path = $this->ui_url . UI_CONSTANTS_API_VER . "/".
                         UI_CONSTANTS_UPDATE_USER_PATH;
      $this->award_badge_path = $this->ui_url . UI_CONSTANTS_API_VER . "/".
                         UI_CONSTANTS_AWARD_BADGE_PATH;
      $this->award_badge_points_path = $this->ui_url . UI_CONSTANTS_API_VER . 
                         "/". UI_CONSTANTS_AWARD_BADGE_POINTS_PATH;
      $this->award_points_path = $this->ui_url . UI_CONSTANTS_API_VER . "/".
                         UI_CONSTANTS_AWARD_POINTS_PATH;
      $this->get_user_data_path = $this->ui_url . UI_CONSTANTS_API_VER . "/".
                         UI_CONSTANTS_GET_USER_DATA_PATH;
      $this->remove_badge_path = $this->ui_url . UI_CONSTANTS_API_VER . "/".
                         UI_CONSTANTS_REMOVE_BADGE_PATH;
      $this->widget_path = $this->ui_url . UI_CONSTANTS_API_VER . "/" .
                         UI_CONSTANTS_WIDGET_PATH;
     }
    /*****************************************
    * Name: enable_local_testing
    * Description: All calls to UserInfuser will be to localhost
    * Parameters: None
    * Returns: Nothing
    * Notes: None
    ****************************************/
    public function enable_local_testing() 
    {
      $this->ui_url = UI_CONSTANTS_LOCAL_TEST;
      $this->update_user_path = $this->ui_url . UI_CONSTANTS_API_VER . "/".
                         UI_CONSTANTS_UPDATE_USER_PATH;
      $this->award_badge_path = $this->ui_url . UI_CONSTANTS_API_VER . "/".
                         UI_CONSTANTS_AWARD_BADGE_PATH;
      $this->award_badge_points_path = $this->ui_url.UI_CONSTANTS_API_VER."/".UI_CONSTANTS_AWARD_BADGE_POINTS_PATH;
      $this->award_points_path = $this->ui_url . UI_CONSTANTS_API_VER . "/".
                         UI_CONSTANTS_AWARD_POINTS_PATH;
      $this->get_user_data_path = $this->ui_url . UI_CONSTANTS_API_VER . "/".
                         UI_CONSTANTS_GET_USER_DATA_PATH;
      $this->remove_badge_path = $this->ui_url . UI_CONSTANTS_API_VER . "/" .
                         UI_CONSTANTS_REMOVE_BADGE_PATH;
      $this->widget_path = $this->ui_url . UI_CONSTANTS_API_VER . "/" .
                         UI_CONSTANTS_WIDGET_PATH;
    }
    /*****************************************
    * Name: only_sync_calls
    * Description: All calls will block for a reply from the server. This
    *              will slow down your application, but may be useful for
    *              debugging.
    * Parameters: None
    * Returns: Nothing
    * Notes: None
    ****************************************/
    public function only_sync_calls()
    {
      $this->only_sync = True;
    }
    /*****************************************
    * Name: get_user_date
    * Description: Gets user data. 
    * Parameters: A user id. It could be an email or some unique name
    * Returns: A dictionary of information about the user. See Notes.
    * Notes: Example output
    *  returns a dictionary of information about the user
    *       example:
    *       {"status": "success", 
    *        "is_enabled": "yes", 
    *        "points": 200, 
    *        "user_id": "nlake44@gmail.com", 
    *        "badges": ["muzaktheme-guitar-private", 
    *                   "muzaktheme-bass-private", 
    *                   "muzaktheme-drums-private"], 
    *        "profile_img": "http://test.com/images/raj.png",
    *        "profile_name": "Raj Chohan", 
    *        "profile_link": "http://test.com/nlake44", 
    *        "creation_date": "2011-02-26"} 
    * This function is always synchronous. It will add latency into 
    * your application/web site. 
    ****************************************/
    public function get_user_data($user_id)
    {
       if ($this->debug){ print "get_user_data with ".$user_id."\n";}
       $argsdict = array("apikey" => $this->api_key,
                         "userid" => $user_id,
                         "accountid" => $this->account);
       $ret = $this->__sync_url_post($this->get_user_data_path, $argsdict);
       
       $json_a=json_decode(stripslashes($ret),True);
       return $json_a;
    }
    /*****************************************
    * Name: update_user
    * Description: Adds a new user or updates a current users information
    * Required Arguments: user_id (unique user identifier)
    * Optional Arguments:
    *                     user_name (The name that will show up in widgets,
    *                                othewise it will use the user_id)
    *                     link_to_profile (a URL to the user's profile)
    *                     link_to_profile (a URL to a user's profile picture) 
    * Return value: True on success, false otherwise 
    ****************************************/
    public function update_user($user_id, $user_name="", $link_to_profile="", $link_to_profile_img="")
    {
      $argsdict = array("apikey" => $this->api_key,
                       "userid" => $user_id,
                       "accountid" => $this->account,
                       "profile_name" => $user_name,
                       "profile_link" => $link_to_profile,
                       "profile_img" => $link_to_profile_img);
      if ($this->only_sync){
        $ret = $this->__sync_url_post($this->update_user_path, $argsdict);
        return $this->__json_ret_check($ret);
      }
      else{
        $this->__async_url_post($this->update_user_path, $argsdict);
        return True;
      }
    } 

    /*****************************************
     * Function: award_badge
     * Description: Award a badge to a user
     * Required Arguments: user_id (unique user identifier)
     *                     badge_id (unique badge identifier from 
     *                               UserInfuser website under badges tab of 
     *                               control panel)
     * Optional Arguments: reason (A short string that shows up in the user's 
     *                             trophy case)
     *                     resource (A URL that the user goes to if the badge 
     *                             is clicked) 
     * Return value: True on success, False otherwise
     ****************************************/
    public function award_badge($user_id, $badge_id, $reason="", $resource="")
    {
      $argsdict = array("apikey"=>$this->api_key,
                        "accountid"=>$this->account,
                        "userid"=>($user_id),
                        "badgeid"=>($badge_id),
                        "reason"=>($reason),
                        "resource"=>$resource);
      if ($this->only_sync){
        $ret =  $this->__sync_url_post($this->award_badge_path, $argsdict);
        return $this->__json_ret_check($ret);
      }
      else{
        $this->__async_url_post($this->award_badge_path, $argsdict);
        return True;
      }
    } 

    /*****************************************
     * Function: remove_badge
     * Description: Remove a badge from a user
     * Required Arguments: user_id (unique user identifier)
     *                     badge_id (unique badge identifier from 
     *                               UserInfuser website under badges tab of 
     *                               control panel)
     * Return value: True on success, False otherwise
     ****************************************/
    public function remove_badge($user_id, $badge_id)
    {
      $argsdict = array("apikey"=>$this->api_key,
                  "accountid"=>$this->account,
                  "userid"=>($user_id),
                  "badgeid"=>($badge_id));
      if ($this->only_sync){
        $ret =  $this->__sync_url_post($this->remove_badge_path, $argsdict);
        return  $this->__json_ret_check($ret);
      }
      else{
        $this->__async_url_post($this->remove_badge_path, $argsdict);
        return True;
      }
    }

    /*****************************************
    * Function: award_points
    * Description: Award points to a user
    * Required Arguments: user_id (unique user identifier)
    *                      points_awarded 
    * Optional Arguments: reason (Why they got points)
    * Return value: True on success, False otherwise
    ****************************************/
    public function award_points($user_id, $points_awarded, $reason="")
    {
      $argsdict = array("apikey"=>$this->api_key,
                       "accountid"=>$this->account,
                       "userid"=>($user_id),
                       "pointsawarded"=>($points_awarded),
                       "reason"=>($reason));
      if ($this->only_sync){
        $ret = $this->__sync_url_post($this->award_points_path, $argsdict);
        return $this->__json_ret_check($ret);
      }
      else{
        $this->__async_url_post($this->award_points_path, $argsdict);
        return True;
      }
    } 

    /*****************************************
    * Function: award_badge_points
    * Description: Award badge points to a user. Badges can also be achieved
    *              after a certain number of points are given towards an 
    *              action. When that number is reached the badge is awarded to
    *              the user. 
    * Required Arguments: user_id (unique user identifier)
    *                  points_awarded 
    *                  badge_id (unique badge identifier from 
    *                               UserInfuser website under badges tab of 
    *                               control panel)
    *                  points_required (The total number of points a user must
    *                               collect to get the badge)
    * Optional Arguments: reason (Why they got the badge points)
    *                     resource (URL link to assign to badge)
    * Return value: True on success, False otherwise
    ****************************************/
    public function award_badge_points($user_id,
                                       $badge_id, 
                                       $points_awarded, 
                                       $points_required, 
                                       $reason="", 
                                       $resource="")
    {
      $argsdict = array("apikey"=>$this->api_key,
                        "accountid"=>$this->account,
                        "userid"=>($user_id),
                        "badgeid"=>($badge_id),
                        "pointsawarded"=>($points_awarded),
                        "pointsrequired"=>($points_required),
                        "reason"=>($reason),
                        "resource"=>$resource);
      if ($this->only_sync){
        $ret = $this->__sync_url_post($this->award_badge_points_path, $argsdict);
        return $this->__json_ret_check($ret);
      }
      else{
        $this->__async_url_post($this->award_badge_points_path, $argsdict);
        return True;
      }
    }
    /*****************************************
    * Function: get_widget
    *  Description: Retrieve the HTML 
    *  Required Arguments: user_id (unique user identifier)
    *                   widget_type (Check website for supported widgets)
    *  Optional Arguments: height and width. It is strongly recommended to 
    *                   tailor these values to your site rather than using 
    *                   the default (500x300 pixels). Wigets like points and 
    *                   rank should be much smaller.
    *  Return value: String to place into your website. The string will 
    *                render an iframe of a set size. Customize your widgets 
    *                on the UserInfuser website.
    ****************************************/
    public function get_widget($user_id, $widget_type, $height=300, $width=500)
    {
      if (!in_array($widget_type, $this->valid_widgets)){
        throw new Exception("Unknown widget type $widget_type\n"); 
      }
      if ($user_id == ""){
        $user_id = UI_CONSTANTS_ANONYMOUS;
      }
      $this->__prefetch_widget($widget_type, $user_id);
      $userhash = sha1($this->account.'---'.$user_id);
      if ($widget_type != "notifier"){
        return "<iframe style='border:none' height='".$height."px' width='".
          $width."px' scrolling='no' allowtransparency='true' src='".$this->widget_path."?widget=".
          $widget_type."&u=".$userhash."&height=".$height."&width=".
          $width."'>Sorry your browser does not support iframes!</iframe>";
      }
      else{
        return "<div style='z-index:9999; overflow: hidden; position: fixed; bottom: 0px; right: 10px;'><iframe style='border:none;' allowtransparency='true' height='".$height."px' width='".$width."px' scrolling='no' src='".$this->widget_path."?widget=".$widget_type."&u=".$userhash."&height=".$height."&width=".$width."'>Sorry your browser does not support iframes!</iframe></div>";
      }
    }
   
    private function __sync_url_post($url, $params)
    {
      if ($this->debug){ 
        print "\nSync url post with ".$url." and ";
        print_r($params);
        print "\n";
      }
      $fields_string = "";
      foreach($params as $key=>$value) 
        { $fields_string .= $key.'='.$value.'&'; }
      rtrim($fields_string,'&');
      //open connection
      $ch = curl_init();

      //set the url, number of POST vars, POST data
      curl_setopt($ch,CURLOPT_URL,$url);
      curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);
      curl_setopt($ch,CURLOPT_POST,count($params));
      curl_setopt($ch,CURLOPT_POSTFIELDS,$fields_string);
      curl_setopt($ch,CURLOPT_TIMEOUT,UI_CONSTANTS_TIMEOUT);

      //execute post
      if ($this->debug){ print "Sync url: ".$url."\n";}
      $result = curl_exec($ch); 
      if ($this->debug){ print "Sync url post result: ".$result."\n";}

      //close connection
      curl_close($ch);
      return $result;
    }
   
    private function __async_url_post($url, $params)
    {
      $params['async'] = "yes";
      foreach ($params as $key => &$val) {
        if (is_array($val)) $val = implode(',', $val);
          $post_params[] = $key.'='.urlencode($val);
      }
      $post_string = implode('&', $post_params);

      $parts=parse_url($url);

      $fp = fsockopen($parts['host'],
          isset($parts['port'])?$parts['port']:80,
          $errno, $errstr, 30);

      $out = "POST ".$parts['path']." HTTP/1.1\r\n";
      $out.= "Host: ".$parts['host']."\r\n";
      $out.= "Content-Type: application/x-www-form-urlencoded\r\n";
      $out.= "Content-Length: ".strlen($post_string)."\r\n";
      $out.= "Connection: Close\r\n\r\n";
      if (isset($post_string)) $out.= $post_string;

      fwrite($fp, $out);
      fclose($fp);
      // This returns nothing, check the online console to see success/failures
    }
    private function __ui_cURLcheckBasicFunctions()
    {
      if( !function_exists("curl_init") &&
        !function_exists("curl_setopt") &&
        !function_exists("curl_exec") &&
        !function_exists("curl_close") ) return false;
      else{ 
        return true;
      }
    } 
    private function __json_ret_check($ret_status)
    {
      $json_a=json_decode($ret_status,true);
      if ($json_a['status'] == 'success'){
        return True;
      }
      else{
        return False ;
      }
    }
    private function __prefetch_widget($widget_type, $user_id)
    {
       if ($this->debug){ print "get_user_data with ".$user_id."\n";}
       $argsdict = array("apikey" => $this->api_key,
                         "accountid"=>$this->account,
                         "userid" => $user_id,
                         "widget" => $widget_type);
       $this->__async_url_post($this->widget_path, $argsdict);
    }
       
  }
?>
