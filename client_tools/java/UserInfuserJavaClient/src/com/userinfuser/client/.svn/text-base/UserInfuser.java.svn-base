/*
 * Copyright 2011, Cloud Captive Inc.
 * 
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at 
 * 
 * http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * 
 * Author: Navraj Chohan and Shan Randhawa
 */

package com.userinfuser.client;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.UnsupportedEncodingException;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.ProtocolException;
import java.net.URL;
import java.net.URLEncoder;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HashMap;
import java.util.Map;

import org.apache.log4j.Logger;

/**
 * Class used to communicate with the UserInfuser server.
 * 
 * @author Shan Randhawa <shan@cloudcaptive.com>
 * @version 1
 * @since 1.5
 */
public class UserInfuser
{
	
	private static final Logger s_logger = Logger.getLogger(UserInfuser.class.getName());
	
	private String f_accountId;
	private String f_apiKey;
	
	private boolean f_encrypt;
	private boolean f_syncAll;
	
	private final static String ENCODING = "UTF-8";
	private final static String HASHING_ALGORITHM = "SHA-1";
	private final static String REQUEST_METHOD = "POST";
	
	private String f_usePath;
	
	/**
	 * Constructor
	 * 
	 * @param accountId The email address that you used to register your
	 *            account.
	 * @param apiKey Unique key that is assigned for your account. This API key
	 *            can be obtained by logging into your account on the web.
	 * 
	 */
	public UserInfuser(final String accountId, final String apiKey)
	{
		f_accountId = accountId;
		f_apiKey = apiKey;
		
		f_syncAll = false;
		
		// not secure by default
		f_encrypt = false;
		f_usePath = Constants.PATH;
		
	}
	
	/**
	 * Constructor
	 * 
	 * @param accountId The email address that you used to register your
	 *            account.
	 * @param apiKey Unique key that is assigned for your account. This API key
	 *            can be obtained by logging into your account on the web.
	 * @param encrypt Use SSL to communicate with server.
	 * @param debug Enable debug mode.
	 * @param local Use this for debugging.
	 * @param syncAll Uses all synchronous calls. Slows down calls to the
	 *            server, use only for testing.
	 * 
	 */
	public UserInfuser(final String accountId, final String apiKey, final boolean encrypt, final boolean debug, final boolean local, final boolean syncAll)
	{
		f_accountId = accountId;
		f_apiKey = apiKey;
		f_syncAll = syncAll;
		f_encrypt = encrypt;
		
		// set path according to whether or not https is desired.
		if (f_encrypt)
		{
			f_usePath = Constants.PATH_SECURE;
		}
		else
		{
			f_usePath = Constants.PATH;
		}
	}
	
	/**
	 * Obtain information about a particular user.
	 * 
	 * Note: This function is always synchronous, it could add latency to your
	 * webapp.
	 * 
	 * @param userId A unique identifier per user. It can be an email, user
	 *            name, etc.
	 * @return A dictionary of user information. For example: <code>
	 * {"status": "success",<br/>
	 * &nbsp;&nbsp;&nbsp;"is_enabled": "yes",<br/>
	 * &nbsp;&nbsp;&nbsp;"points": 200,<br/>
	 * &nbsp;&nbsp;&nbsp;"user_id": "nlake44@gmail.com",<br/>
	 * &nbsp;&nbsp;&nbsp;"badges":  ["muzaktheme-guitar-private",<br/>
	 * &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"muzaktheme-bass-private",<br/>
	 * &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"muzaktheme-drums-private"],<br/>
	 * &nbsp;&nbsp;&nbsp;"profile_img": "http://test.com/images/raj.png",<br/>
	 * &nbsp;&nbsp;&nbsp;"profile_name": "Raj Chohan",<br/>
	 * &nbsp;&nbsp;&nbsp;"profile_link": "http://test.com/nlake44",<br/>
	 * &nbsp;&nbsp;&nbsp;"creation_date": "2011-02-26"}<br/>
	 * </code>
	 * 
	 */
	public String getUserInfo(final String userId)
	{
		final Map<String, String> params = new HashMap<String, String>();
		
		params.put("apikey", f_apiKey);
		params.put("userid", userId);
		params.put("accountid", f_accountId);
		
		return doPost(f_usePath + Constants.API_VERSION + "/" + Constants.PATH_GET_USER_DATA, params);
	}
	
	/**
	 * To add user. Or update user information.
	 * 
	 * @param userId A unique identifier per user. It can be an email, user
	 *            name, etc.
	 * @return True on success, false otherwise.
	 */
	public boolean updateUser(final String userId)
	{
		return updateUser(userId, null, null, null);
	}
	
	/**
	 * To add user. Or update user information.
	 * 
	 * @param userId A unique identifier per user. It can be an email, user
	 *            name, etc.
	 * @param userName The name that will show up on users' widgets, otherwise
	 *            userid will be displayed.
	 * @param linkToProfile URL to the user's profile
	 * @param linkToProfileImage URL to the user's profile image
	 * @return True on success, false otherwise.
	 */
	public boolean updateUser(final String userId, String userName, String linkToProfile, String linkToProfileImage)
	{
		if (userId == null)
		{
			return false;
		}
		
		userName = (userName == null) ? "" : userName;
		linkToProfile = (linkToProfile == null) ? "" : linkToProfile;
		linkToProfileImage = (linkToProfileImage == null) ? "" : linkToProfileImage;
		
		final Map<String, String> params = new HashMap<String, String>();
		
		params.put("apikey", f_apiKey);
		params.put("userid", userId);
		params.put("accountid", f_accountId);
		params.put("profile_name", userName);
		params.put("profile_link", linkToProfile);
		params.put("profile_img", linkToProfileImage);
		
		String targetPath = f_usePath + Constants.API_VERSION + "/" + Constants.PATH_UPDATE_USER;
		final String response = doPost(targetPath, params);
		
		return true;
	}
	
	/**
	 * Award a badge to a user
	 * 
	 * @param userId A unique identifier per user. It can be an email, user
	 *            name, etc.
	 * @param badgeId A unique identifier for a badge. Badge IDs are available
	 *            on the admin console online.
	 * @return true on success.
	 */
	public boolean awardBadge(final String userId, final String badgeId)
	{
		return awardBadge(userId, badgeId, null, null);
	}
	
	/**
	 * Award a badge to a user
	 * 
	 * @param userId A unique identifier per user. It can be an email, user
	 *            name, etc.
	 * @param badgeId A unique identifier for a badge. Badge IDs are available
	 *            on the admin console online.
	 * @param reason A short string that will appear on the trophy case for the
	 *            awarded badge.
	 * @param resource A URL that the user will link to if the badge is clicked
	 * @return true on success.
	 */
	public boolean awardBadge(final String userId, final String badgeId, String reason, String resource)
	{
		if (userId == null || badgeId == null)
		{
			return false;
		}
		
		reason = (reason == null) ? "" : reason;
		resource = (resource == null) ? "" : resource;
		
		final Map<String, String> params = new HashMap<String, String>();
		
		params.put("apikey", f_apiKey);
		params.put("userid", userId);
		params.put("accountid", f_accountId);
		params.put("badgeid", badgeId);
		params.put("reason", reason);
		params.put("resource", resource);
		
		String targetPath = f_usePath + Constants.API_VERSION + "/" + Constants.PATH_AWARD_BADGE;
		final String response = doPost(targetPath, params);
		
		return true;
	}
	
	/**
	 * Remove a badge for specified user
	 * 
	 * @param userId A unique identifier per user. It can be an email, user
	 *            name, etc.
	 * @param badgeId A unique identifier for a badge. Badge IDs are available
	 *            on the admin console online.
	 * @return true on success.
	 */
	public boolean removeBadge(final String userId, final String badgeId)
	{
		if (userId == null || badgeId == null)
		{
			return false;
		}
		
		final Map<String, String> params = new HashMap<String, String>();
		
		params.put("apikey", f_apiKey);
		params.put("userid", userId);
		params.put("accountid", f_accountId);
		params.put("badgeid", badgeId);
		
		final String targetPath = f_usePath + Constants.API_VERSION + "/" + Constants.PATH_REMOVE_BADGE;
		final String response = doPost(targetPath, params);
		
		return true;
	}
	
	/**
	 * Award a user points
	 * 
	 * @param userId A unique identifier per user. It can be an email, user
	 *            name, etc.
	 * @param pointsAwarded Points to award.
	 * @return true on success.
	 */
	public boolean awardPoints(final String userId, final int pointsAwarded)
	{
		return awardPoints(userId, pointsAwarded, null);
	}
	
	/**
	 * Award a user points
	 * 
	 * @param userId A unique identifier per user. It can be an email, user
	 *            name, etc.
	 * @param pointsAwarded Points to award.
	 * @param reason Reason points are being awarded.
	 * @return true on success.
	 */
	public boolean awardPoints(final String userId, final int pointsAwarded, String reason)
	{
		if (userId == null)
		{
			return false;
		}
		
		reason = (reason == null) ? "" : reason;
		
		final Map<String, String> params = new HashMap<String, String>();
		
		params.put("apikey", f_apiKey);
		params.put("userid", userId);
		params.put("accountid", f_accountId);
		params.put("reason", reason);
		params.put("pointsawarded", Integer.toString(pointsAwarded));
		
		final String targetPath = f_usePath + Constants.API_VERSION + "/" + Constants.PATH_AWARD_POINTS;
		final String response = doPost(targetPath, params);
		
		return true;
	}
	
	/**
	 * Award badge points to a user. Badges can also be achieved after a certain
	 * number of points are given towards an action. When that number is reached
	 * the badge awarded to the user.
	 * 
	 * @param userId A unique identifier per user. It can be an email, user
	 *            name, etc.
	 * @param pointsAwarded Points to award.
	 * @param badgeId A unique identifier for a badge. Badge IDs are available
	 *            on the admin console online.
	 * @param pointsRequired The total number of points a user must collect to
	 *            get the badge.
	 * 
	 * @return true on success.
	 */
	public boolean awardBadgePoints(final String userId, final int pointsAwarded, final String badgeId, final int pointsRequired)
	{
		return awardBadgePoints(userId, pointsAwarded, badgeId, pointsRequired, null, null);
	}
	
	/**
	 * Award badge points to a user. Badges can also be achieved after a certain
	 * number of points are given towards an action. When that number is reached
	 * the badge awarded to the user.
	 * 
	 * @param userId A unique identifier per user. It can be an email, user
	 *            name, etc.
	 * @param pointsAwarded Points to award.
	 * @param badgeId A unique identifier for a badge. Badge IDs are available
	 *            on the admin console online.
	 * @param pointsRequired The total number of points a user must collect to
	 *            get the badge.
	 * @param reason A short string that will appear on the trophy case for the
	 *            awarded badge.
	 * @param resource A URL that the user will link to if the badge is clicked
	 * 
	 * @return true on success.
	 */
	public boolean awardBadgePoints(final String userId, final int pointsAwarded, final String badgeId, final int pointsRequired, String reason, String resource)
	{
		if (userId == null || badgeId == null)
		{
			return false;
		}
		
		reason = (reason == null) ? "" : reason;
		resource = (resource == null) ? "" : resource;
		
		final Map<String, String> params = new HashMap<String, String>();
		
		params.put("apikey", f_apiKey);
		params.put("userid", userId);
		params.put("accountid", f_accountId);
		params.put("reason", reason);
		params.put("resource", resource);
		params.put("badgeid", badgeId);
		params.put("pointsawarded", Integer.toString(pointsAwarded));
		params.put("pointsrequired", Integer.toString(pointsRequired));
		
		final String targetPath = f_usePath + Constants.API_VERSION + "/" + Constants.PATH_AWARD_BADGE_POINTS;
		final String response = doPost(targetPath, params);
		
		return true;
	}
	
	/**
	 * Retrieve the HTML
	 * 
	 * @param userId A unique identifier per user. It can be an email, user
	 *            name, etc.
	 * @param widgetType Specify the widget that you want rendered. Use
	 *            WidgetType enum.
	 * @return A string to place into your website. The string will render an
	 *         iframe of a set size. Customize your widgets on the UserInfuser
	 *         website.
	 */
	public String getWidget(final String userId, final WidgetType widgetType)
	{
		return _getWidget(userId, widgetType, "", "");
	}
	
	/**
	 * Retrieve the HTML, with height and width specified.
	 * 
	 * @param userId A unique identifier per user. It can be an email, user
	 *            name, etc. If not specified a default widget will be returned.
	 * @param widgetType Specify the widget that you want rendered. Use
	 *            WidgetType enum.
	 * @param height Specify height of widget.
	 * @param width Specify width of widget.
	 * @return A string to place into your website. The string will render an
	 *         iframe of a set size. Customize your widgets on the UserInfuser
	 *         website. Will return null in case of error.
	 */
	public String getWidget(final String userId, final WidgetType widgetType, final int height, final int width)
	{
		return _getWidget(userId, widgetType, Integer.toString(height), Integer.toString(width));
	}
	
	private String _getWidget(String userId, final WidgetType widgetType, final String height, final String width)
	{
		if (userId == null || userId.equals(""))
		{
			userId = Constants.UI_ANONYMOUS;
		}
		MessageDigest md = null;
		try
		{
			md = MessageDigest.getInstance(HASHING_ALGORITHM);
		}
		catch (NoSuchAlgorithmException e)
		{
			s_logger.info("NoSuchAlgorithmException caught. Failed to get instance of MessageDigest with algorithm: " + HASHING_ALGORITHM);
		}
		
		byte[] digest = md.digest((f_accountId + "---" + userId).getBytes());
		final String hashedArg = bytes2String(digest);
		final String widgetPath = f_usePath + Constants.API_VERSION + "/" + Constants.PATH_WIDGET;
		
		if (widgetType != WidgetType.NOTIFIER)
		{
			return "<iframe style='border:none' height='" + height + "px' width='" + width + "px' allowtransparency='true' scrolling='no' src='" + widgetPath + "?widget=" + widgetType.getName() + "&u=" + hashedArg + "&height=" + height + "&width=" + width + "'>Sorry your browser does not support iframes!</iframe>";
		}
		else
		{
			return "<script type='text/javascript' src=" + widgetPath + "?widget=" + widgetType.getName() + "&u=" + hashedArg + "&height=" + height + "&width=" + width + "&t=outside'></script> <iframe src='" + widgetPath + "?widget=" + widgetType.getName() + "&u=" + hashedArg + "&height=" + height + "&width=" + width + "&t=inside width=\"0\" height=\"0\" frameborder=\"0\" allowtransparency='true' scrolling=\"no\" name=\"ui__notifier\"'>Your browser is not supported. Sorry!</iframe>";
		}
		
	}
	
	private static String bytes2String(byte[] bytes)
	{
		StringBuilder string = new StringBuilder();
		for (byte b : bytes)
		{
			String hexString = Integer.toHexString(0x00FF & b);
			string.append(hexString.length() == 1 ? "0" + hexString : hexString);
		}
		return string.toString();
	}
	
	private String doPost(final String url, final Map<String, String> params)
	{
		String response = null;
		if (f_syncAll)
		{
			s_logger.debug("Executing synchronous post.");
			response = _doPost(url, params);
		}
		else
		{
			s_logger.debug("Executing asynchronous post.");
			Thread postThread = new Thread(new AsyncPost(url, params));
			postThread.start();
		}
		return response;
	}
	
	private String _doPost(final String urlStr, final Map<String, String> params)
	{
		String paramsStr = "";
		for (String key : params.keySet())
		{
			try
			{
				paramsStr += URLEncoder.encode(key, ENCODING) + "=" + URLEncoder.encode(params.get(key), ENCODING) + "&";
			}
			catch (UnsupportedEncodingException e)
			{
				s_logger.debug("UnsupportedEncodingException caught. Trying to encode: " + key + " and " + params.get(key));
				return null;
			}
		}
		
		if (paramsStr.length() == 0)
		{
			s_logger.debug("POST will not complete, no parameters specified.");
			return null;
		}
		
		s_logger.debug("POST to server will be done with the following parameters: " + paramsStr);
		
		HttpURLConnection connection = null;
		String responseStr = null;
		try
		{
			connection = (HttpURLConnection) (new URL(urlStr)).openConnection();
			connection.setRequestMethod(REQUEST_METHOD);
			connection.setDoOutput(true);
			DataOutputStream dos = new DataOutputStream(connection.getOutputStream());
			dos.write(paramsStr.getBytes());
			dos.flush();
			dos.close();
			
			InputStream is = connection.getInputStream();
			BufferedReader rd = new BufferedReader(new InputStreamReader(is));
			String line;
			StringBuffer response = new StringBuffer();
			while ((line = rd.readLine()) != null)
			{
				response.append(line);
				response.append('\r');
			}
			
			rd.close();
			responseStr = response.toString();
			
		}
		catch (ProtocolException e)
		{
			s_logger.debug("ProtocolException caught. Unable to execute POST.");
		}
		catch (MalformedURLException e)
		{
			s_logger.debug("MalformedURLException caught. Unexpected. Url is: " + urlStr);
		}
		catch (IOException e)
		{
			s_logger.debug("IOException caught. Unable to execute POST.");
		}
		
		return responseStr;
	}
	
	private class AsyncPost implements Runnable
	{
		
		private String f_url;
		private Map<String, String> f_params;
		
		public AsyncPost(final String url, final Map<String, String> params)
		{
			f_url = url;
			f_params = params;
		}
		
		public void run()
		{
			_doPost(f_url, f_params);
		}
		
	}
}
