<?php 
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

$prime_path = "http://localhost:8080/api/1/test";
$delete_path = "http://localhost:8080/api/1/testcleanup";
# ID settings for testing
$account = "a@a.a";
$testId = "testuserid";
$badgeId1 = "music-1-private";
$badgeId2 = "music-2-private";
$badgeId3 = "music-3-private";
$testSecret = "8u8u9i9i";
# Set API key
$apiKey = "ABCDEFGHI";
$DEFAULT_DEBUG = True;
# Turn this off/on to leave or delete data from the db 
$cleanup = False;
$debug = $DEFAULT_DEBUG;
function __sync_url_post($url, $params)
{
  global $debug;
  if ($debug){ print "sync url post with ".$url." and ".$params."\n";}
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
  curl_setopt($ch,CURLOPT_TIMEOUT,10);

  //execute post
  $result = curl_exec($ch); 
  //close connection
  curl_close($ch);
  if ($debug){ print "sync url post result: ".$result."\n";}
  return $result;
}
//""" Make sure what we received is what we expected """
function checkerr($line_num, $received, $expected)
{
  $file = $_SERVER['SCRIPT_NAME'];   
  if ($expected != $received){
    # TODO  write this test script to get full coverage
    print "Failed for test at " . $file . ": " . $line_num . 
          " with a return of: " . $received. " while expecting: " .$expected;
    exit(1);
  }
}
//""" Make sure the item is not what we received """
function notcheckerr($line_num, $received, $shouldnotbe)
{
  if ($shouldnotbe == $received){
    print "Failed for test at " . $file . ": " . $line_num
        . " with a return of: " . $received .
        " while it should not be but was: " . $shouldnotbe;
    exit(1);
  }
}
function checkstrmatch($line_num, $ret, $search)
{
  $file = $_SERVER['SCRIPT_NAME'];   
  if ($ret != $search){
    print "Failed for test at " . $file. ":" . $line_num
        . " with a return of: " . $ret.
        " while searching for: " . $search."\n";
    exit(1);
  }
}
//""" See if the given string is contained in the response """
function checkstr($line_num, $received, $searchstr)
{
  $file = $_SERVER['SCRIPT_NAME'];   
  if (!strpos($received, $searchstr)){
    print "Failed for test at " . $file. ":" . $line_num
        . " with a return of: " . $received .
        " while searching for: " . $searchstr."\n";
    exit(1);
  }
}
//""" See if the given string is contained in the response """
function checkjson($line_num, $received, $searchstr)
{
  $file = $_SERVER['SCRIPT_NAME'];   
  if (strcmp($received['status'], $searchstr) != 0){
    print "Failed for test at " . $file. ":" . $line_num
        . " with a return of: " . implode(",",$received) .
        " while comparing: " . $searchstr;
    exit(1);
  }
}//""" See if the given string is not contained in the response """
function checknotstr($line_num, $received, $searchstr)
{
  if (!strpos((string)$received, $searchstr)){
    return;
  }
  else{
    print "Failed for test at " . $file . ":" . $line_num
        . " with a return of: " + str($received).
        " while searching for: " . $searchstr . " where it should not be";
    exit(1);
  }
}      
function lineno(){
  $debug = debug_backtrace();
  #print_r ($debug);
  return $debug[0]['line'];
}

$badgetheme1 = "music";
$badgetheme2 = "birds";
# Prime the DB with an account and badges
$argsdict = array("apikey"=>$apiKey,
                 "accountid"=>$account,
                 "badgeid"=>$badgeId1,
                 "secret"=>$testSecret,
                 "user"=>$testId,
                 "theme"=>$badgetheme1);

$ret = __sync_url_post($prime_path, $argsdict);
checkstr(lineno(), $ret, "success");
$ret = __sync_url_post($delete_path, $argsdict);
checkstr(lineno(), $ret, "success");
$ret = __sync_url_post($prime_path, $argsdict);
checkstr(lineno(), $ret, "success");

include('userinfuser/ui_api.php');

$gi = new UserInfuser($account, $apiKey);
$ui_bad = new UserInfuser($account . "x", $apiKey . "x");
$ui_bad2 = new UserInfuser($account, $apiKey . "x");
$ui_bad->enable_local_testing();
$ui_bad->enable_debug();
$ui_bad->only_sync_calls();
$ui_bad2->enable_local_testing();
$ui_bad2->enable_debug();
$ui_bad2->only_sync_calls();
$gi->enable_local_testing();
$gi->enable_debug();
$gi->only_sync_calls();
$gi->get_user_data("user_no_exist");
checkjson(lineno(), $gi->get_user_data("user_no_exist"), "failed");
# Test with non existing account and api key
$start = microtime();
checkerr(lineno(), $ui_bad->update_user("user_no_exist"), False);
$sync_call_time = microtime() - $start; 
checkjson(lineno(), $ui_bad->get_user_data("user_no_exist"), "failed");
# Test with bad api key, but good account
checkjson(lineno(), $ui_bad2->get_user_data("user_no_exist"), "failed");
checkerr(lineno(), $ui_bad2->update_user("user_no_exist"), False);

checkerr(lineno(), $gi->update_user($testId), True);
checkerr(lineno(), $gi->update_user($testId, "Raj"), True); 
checkerr(lineno(), $gi->update_user($testId, "Raj", 'http://facebook.com/nlake44', 'http://www.facebook.com/nlake44'), True);
checkjson(lineno(), $gi->get_user_data($testId), "success");
checkstr(lineno(), implode(",",$gi->get_user_data($testId)), "facebook");
checkerr(lineno(), $ui_bad->award_badge_points($testId, $badgeId1, 10, 100, "Promoter"), False);
checkerr(lineno(), $ui_bad2->award_badge_points($testId, $badgeId1, 10, 100, "Promoter"), False);

checkerr(lineno(), $gi->award_badge_points($testId, $badgeId1, 10, 100, "Promoter"), True);
checknotstr(lineno(), $gi->get_user_data($testId), $badgeId1);
checkerr(lineno(), $gi->award_badge_points($testId, $badgeId1, 90, 100, "Promoter"), True);
$ret = $gi->get_user_data($testId);
$retbadge = $ret['badges'][0];
checkstrmatch(lineno(), $retbadge, $badgeId1);

checkerr(lineno(), $ui_bad->award_badge($badgeId1, "user_no_exist"), False);
checkerr(lineno(), $ui_bad->award_badge($badgeId1, "user_no_exist", "best comment"), False);
checkerr(lineno(), $ui_bad2->award_badge($badgeId1, "user_no_exist"), False);
checkerr(lineno(), $ui_bad2->award_badge($badgeId1, "user_no_exist", "top notch"), False);
checkerr(lineno(), $gi->award_badge("bad-badge", "user_no_exist"), False);
checkerr(lineno(), $gi->award_badge("bad-badge-holler", "user_no_exist"), False);
checkerr(lineno(), $gi->award_badge($testId, ""), False);
checkerr(lineno(), $gi->award_badge( $testId, "","Sharing is Caring"), False);
checkerr(lineno(), $gi->award_badge($testId,$badgeId3,  "Sharing is Caring"), True);

checkerr(lineno(), $gi->award_badge_points($testId, $badgeId2, 10, 100, "Promoter"), True);
checknotstr(lineno(), $gi->get_user_data($testId), $badgeId2);
checkerr(lineno(), $gi->award_badge_points($testId, $badgeId2, 90, 100, "Promoter"), True);
$ret = $gi->get_user_data($testId);
$retbadge = $ret['badges'];
$retbadge = implode(',',$retbadge);
checkstr(lineno(), $retbadge , $badgeId2);

checkerr(lineno(), $ui_bad->remove_badge("user_no_exist", $badgeId1), False);
checkerr(lineno(), $gi->remove_badge("user_no_exist", $badgeId1."x"), False);
checkerr(lineno(), $gi->remove_badge($testId, $badgeId1 + "x" ), False);
checkerr(lineno(), $ui_bad->remove_badge("user_no_exist", $badgeId1."x"), False);
checkerr(lineno(), $ui_bad2->remove_badge("user_no_exist", $badgeId1), False);
checkerr(lineno(), $ui_bad2->remove_badge("user_no_exist", $badgeId1), False);
checkerr(lineno(), $ui_bad2->remove_badge($testId, $badgeId1 + "x"), False);
checkerr(lineno(), $gi->remove_badge($testId,$badgeId1), True);
checknotstr(lineno(), $gi->get_user_data($testId), $badgeId1);

checkerr(lineno(), $ui_bad->award_points($testId, 10, "Shared with a friend"), False);
checkerr(lineno(), $ui_bad2->award_points($testId, 10, "Shared with a friend"), False);
checkerr(lineno(), $gi->award_points($testId, "hello", "Shared with a friend"), False);
checkerr(lineno(), $gi->award_points($testId, 10, "Shared with a friend"), True);

$ret = __sync_url_post($delete_path, $argsdict);
checkstr(lineno(), $ret, "success");
$ret = __sync_url_post($prime_path, $argsdict);
checkstr(lineno(), $ret, "success");
checkjson(lineno(), $gi->get_user_data($testId), "failed");
# Make sure the user now exist
checkerr(lineno(), $gi->award_points($testId, 10, "Shared with a friend"), True);
checkjson(lineno(), $gi->get_user_data($testId), "success");
$ret = $gi->get_user_data($testId);
$ret = $ret['points'];
checkstrmatch(lineno(), $ret, "10");
checkerr(lineno(), $gi->award_points($testId, 10, "Shared with a friend"), True);
$ret = $gi->get_user_data($testId);
$ret = $ret['points'];
checkstrmatch(lineno(), $ret, "20");
checkstr(lineno(), $gi->get_widget($testId, "trophy_case", 100,100),"100");
print $gi->get_widget($testId, "rank", 400,200);
print $gi->get_widget($testId, "notifier", 400,200);
print $gi->get_widget($testId, "trophy_case", 400,200);
print $gi->get_widget($testId, "points", 400,200);
print $gi->get_widget($testId, "leaderboard", 400,200);
print $gi->get_widget($testId, "milestones", 400,200);
print "ANONYMOUS WIDGETS";
print $gi->get_widget("", "rank", 400,200);
print $gi->get_widget("", "notifier", 400,200);
print $gi->get_widget("", "trophy_case", 400,200);
print $gi->get_widget("", "points", 400,200);
print $gi->get_widget("", "leaderboard", 400,200);
print $gi->get_widget("", "milestones", 400,200);


$gi = new UserInfuser($account, $apiKey);
$ui_bad = new UserInfuser($account . "x", $apiKey . "x");
$ui_bad->enable_local_testing();
$ui_bad->enable_debug();
$gi->enable_local_testing();
$gi->enable_debug();

$ret = __sync_url_post($prime_path, $argsdict);
checkstr(lineno(), $ret, "success");
$ret = __sync_url_post($delete_path, $argsdict);
checkstr(lineno(), $ret, "success");
$ret = __sync_url_post($prime_path, $argsdict);
checkstr(lineno(), $ret, "success");

checkjson(lineno(), $gi->get_user_data("user_no_exist"), "failed");
# Test with non existing account and api key
checkerr(lineno(), $ui_bad->update_user("user_no_exist"), True);
checkjson(lineno(), $ui_bad->get_user_data("user_no_exist"), "failed");
# Test with bad api key, but good account

checkerr(lineno(), $gi->update_user($testId), True);
checkerr(lineno(), $gi->update_user($testId, "John Smith"), True); 

$start = microtime();
checkerr(lineno(), $gi->update_user($testId, "John Smith", 'http://facebook.com/nlake44', "http://profile.ak.fbcdn.net/hprofile-ak-snc4/203059_3610637_6604695_q.jpg"), True);
$async_call_time = microtime() - $start; 
if ($sync_call_time < $async_call_time){
  print "Sync time is greater than async time";
  print "Sync time:".$sync_call_time;
  print "Async time:".$async_call_time;
  exit(1);
}
checkjson(lineno(), $gi->get_user_data($testId), "success");
$ret = $gi->get_user_data($testId);
$ret = implode(',',$ret);
checkstr(lineno(), $ret, "facebook");
checkerr(lineno(), $ui_bad->award_badge_points($testId,$badgeId1,  10, 100, "Promoter"), True);

checkerr(lineno(), $gi->award_badge_points($testId,$badgeId1,  10, 100, "Promoter"), True);
checknotstr(lineno(), $gi->get_user_data($testId), $badgeId1);
checkerr(lineno(), $gi->award_badge_points($testId, $badgeId1, 90, 100, "Promoter"), True);
$ret = $gi->get_user_data($testId);
$ret = implode(',',$ret['badges']);
checkstrmatch(lineno(), $ret, $badgeId1);

checkerr(lineno(), $ui_bad->award_badge("user_no_exist",$badgeId1 ), True);
checkerr(lineno(), $ui_bad->award_badge("no", $badgeId1, "best comment"), True);
checkerr(lineno(), $gi->award_badge("nouser", "bad-badge"), True);
checkerr(lineno(), $gi->award_badge("nouser", "bad-badge-holler"), True);
checkerr(lineno(), $gi->award_badge("", $testId), True);
checkerr(lineno(), $gi->award_badge("", $testId, "Sharing is Caring"), True);
checkerr(lineno(), $gi->award_badge($testId, $badgeId3, "Sharing is Caring"), True);

checkerr(lineno(), $gi->award_badge_points($testId, $badgeId2, 10, 100, "Promoter"), True);
checknotstr(lineno(), $gi->get_user_data($testId), $badgeId2);
checkerr(lineno(), $gi->award_badge_points($testId, $badgeId2, 90, 100, "Promoter"), True);

$ret = $gi->get_user_data($testId);
$ret = implode(',',$ret['badges']);
checkstr(lineno(), $ret, $badgeId2);

checkerr(lineno(), $ui_bad->remove_badge("user_no_exist", $badgeId1), True);
checkerr(lineno(), $gi->remove_badge("user_no_exist", $badgeId1."x"), True);
checkerr(lineno(), $gi->remove_badge($testId, $badgeId1 + "x"), True);
checkerr(lineno(), $ui_bad->remove_badge("user_no_exist", $badgeId1."x"), True);
checkerr(lineno(), $gi->remove_badge($testId, $badgeId1), True);
checknotstr(lineno(), $gi->get_user_data($testId), $badgeId1);

checkerr(lineno(), $ui_bad->award_points($testId, 10, "Shared with a friend"), True);
checkerr(lineno(), $gi->award_points($testId, "hello", "Shared with a friend"), True);
checkerr(lineno(), $gi->award_points($testId, 10, "Shared with a friend"), True);


if ($cleanup){
  $ret = __sync_url_post($delete_path, $argsdict);
  checkstr(lineno(), $ret, "success");
}

print "Success!\n";
exit(0);
?>
