function editValue(id, value, saveButtonId, inputId, actionId, tdId, entityType) {
	//alert("id: " + id + " and value: " + value);
	$("#" + tdId).empty();
	$("#" + tdId).append(
			"<input value=\"" + value + "\" id=\"" + inputId + "\"/>");
	
	$("#" + actionId).empty();
	$("#" + actionId).append("<button id=\"" + saveButtonId +"\" class=\"button button-gray\" onclick=\"saveFeatureProperty('" + id + "','" + inputId + "', '" + actionId + "', '" + saveButtonId + "', '" + tdId + "' , '" + entityType +"')\"><span class=\"accept\"></span>Save</button>");
}


function saveFeatureProperty(featureId, inputId, actionId, saveButtonId, tdId, entityType) {
	// alert("ID: " + inputId + ". VALUE: " + $("#" + inputId).val());
	
	// Check to see if widget type is notifer... if so, get new token
	getNewNotifierToken();
	
	
	var valueFromId = $("#" + inputId).val();
	
	$.ajax({
		type: "POST",
		url: "/adminconsole/features/update",
		data: "property=" + featureId + "&propertyValue=" + valueFromId + "&entityType=" + entityType,
		success: function(msg){
			//
		}
	});
	
	// now reload the data
	$.ajax({
		  type: "GET",
		  url: "/adminconsole/features/getvalue?of=" + featureId + "&entityType=" + entityType,
		  success: function(reloadedValue){
			  $("#" + tdId).empty();
			  $("#" + tdId).append(reloadedValue);
			  $("#" + actionId).empty();
			  $("#" + actionId).append("<button class=\"button button-gray\" onclick=\"editValue('" + featureId + "','" + reloadedValue + "','" + saveButtonId + "', '" + inputId + "','" + actionId +"', '" + tdId + "','"+entityType+"')\"><span class=\"pencil\"></span>Edit</button>");
		  }
		});    
}

function getNewNotifierToken()
{
	//alert("get new token");
	//get new client token because a value has been updated...
	$.ajax({
		  type: "GET",
		  url: "/adminconsole/newnotifytoken",
		  success: function(value){
			  $("#notifier").empty();
			  $("#notifier").append(value);
		  }
		});   
	
}

function showNotifier()
{
	//alert("show notify!");
	$.ajax({
		  type: "GET",
		  url: "/adminconsole/notify",
		  success: function(value){
			  
		  }
		});   	
}

function deleteBadge(bk)
{
	$.ajax({
		type: "POST",
		url: "/adminconsole/deletebadge",
		data: "bk=" + bk,
                dataType: 'json',
		success: function(data){
	  		if (data.success == true){
         			window.location.reload();
        	        }
            	  	else{
               		   alert(data.reason);
                	}
                }
	});
	
}
