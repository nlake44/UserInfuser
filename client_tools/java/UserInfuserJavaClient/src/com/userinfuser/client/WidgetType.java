package com.userinfuser.client;


public enum WidgetType {
	TROPHY_CASE ("trophy_case"),
	MILESTONES("milestones"),
	NOTIFIER("notifier"),
	POINTS("points"),
	RANK("rank"),
	LEADERBOARD("leaderboard"),
	AVAILABLE_BADGES("availablebadges");
	
	private final String f_name;
	WidgetType(final String name){
		f_name = name;
	}
	
	public String getName(){
		return f_name;
	}
}
