package com.userinfuser.client.test;

import java.io.IOException;
import java.util.Date;

import com.userinfuser.client.UserInfuser;
import com.userinfuser.client.WidgetType;

public class ClientTest
{
	
	private final static String USER_ID_1 = "shanaccount_user1";
	private final static String USER_ID_2 = "shanaccount_user2";
	private final static String USER_ID_3 = "shanaccount_user3";
	private final static String USER_ID_4 = "shanaccount_user4";
	private final static String USER_ID_5 = "shanaccount_user5";
	private final static String USER_ID_6 = "shanaccount_user6";
	
	private final static String ACCOUNT_ID = "shanrandhawa@gmail.com";
	private final static String API_KEY = "a9aabacd-822a-4d48-9d84-1b19f830a505";
	
	private static UserInfuser f_userInfuserModule;
	
	private static void createUserAccount() throws IOException
	{
		// Create users in target account
		f_userInfuserModule.updateUser(USER_ID_4 + new Date().getTime());
	}
	
	protected static void testAnonymousGetWidget() throws Exception
	{
		String widget = f_userInfuserModule.getWidget(null, WidgetType.TROPHY_CASE);
		
		System.out.println("the widget: " + widget);
	}
	
	public static void main(String[] args) throws Exception
	{
		
		f_userInfuserModule = new UserInfuser(ACCOUNT_ID, API_KEY, false, false, false, true);
		
		createUserAccount();
		
		testAnonymousGetWidget();
		
	}
	
}
