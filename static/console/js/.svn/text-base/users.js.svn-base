
function removeUser(userId)
{
  $('#loader').show();
  var a = 0;
  $.ajax({
    type: "POST",
    url: "/adminconsole/users/delete",
    data: "id=" + userId,
    dataType: 'json',
    success: function(data){
      $('#loader').hide();
      if (data.success == true){
         // want to just do $('#' + userId).remove(), but the userId may not be a valid tag (i.e., contains '@')
         // will need to do regex
         window.location.reload();
      }
      else{
         alert(data.reason);
      }
    },
    error: function(request, error){
      $('#loader').hide();
      alert(error);
    }
  });
}

$("#usersOrderedByNameSection").ready(function(){
	// do ajax to get contacts
        $('#loader').show();
	$.getJSON('/adminconsole/users/fetch?page=0&limit=10&orderby=userid',"", function(data){
                $('#loader').hide();
		$.each(data.users, function(i,item){
                        $("#ByNameMessage").remove();
			$("#usersOrderedByNameTBody").append("<tr id='" + item.userid + "'>" +
			  "<td><a href=\"/adminconsole/users/edit?name=" + item.userid + "\">" + item.userid + "</a></td>" +
			  "<td>" + item.points + "</td>" +
                          "<td>" + 
                          "<button class='button button-gray' onclick='removeUser(\"" + item.userid + "\");'><span class='bin'></span>Delete</button>" +
                          "</td>" + 
                           "</tr>");
		});
	})
})

$("#usersOrderedByPointsSection").ready(function(){
        $('#loader').show();
	$.getJSON('/adminconsole/users/fetch?page=0&limit=10&orderby=points',"", function(data){
                $('#loader').hide();
		$.each(data.users, function(i,item){
                        $("#ByPointsMessage").remove();
			$("#usersOrderedByPointsTBody").append("<tr id='" + item.userid +"'>" +
					"<td><a href=\"/adminconsole/users/edit?name=" + item.userid + "\">" + item.userid + "</a></td>" +
					"<td>" + item.points + "</td>" +
                          "<td>" + 
                          "<button class='button button-gray' onclick='removeUser(\"" + item.userid + "\");'><span class='bin'></span>Delete</button>" +
                          "</td>" + 
                           "</tr>");
		});
	})
})

		
function getMoreByName(pageNumber)
{
	// do ajax and get more contacts for specified page number
        $('#loader').show();
	$.getJSON("/adminconsole/users/fetch?page="+pageNumber+"&limit=10&orderby=userid","", function(data){		
                $('#loader').hide();
		$.each(data.users, function(i,item){
			$("#usersOrderedByNameTBody").append("<tr id='" + item.userid + "'>" +
					"<td><a href=\"/adminconsole/users/edit?name=" + item.userid + "\">" + item.userid + "</a></td>" +
					"<td>" + item.points + "</td>" + 
                          "<td>" + 
                          "<button class='button button-gray' onclick='removeUser(\"" + item.userid + "\");'><span class='bin'></span>Delete</button>" +
                          "</td>" + 
                           "</tr>");
		});
	})
	pageNumber++;
	$("#getMoreByName").empty().append("<button class=\"button button-gray\" onclick=\"getMoreByName("+pageNumber+")\">See more</button>");
}

function getMoreByPoints(pageNumber)
{
	// do ajax and get more contacts for specified page number
        $('#loader').show();
	$.getJSON("/adminconsole/users/fetch?page="+pageNumber+"&limit=10&orderby=points","", function(data){		
                $('#loader').hide();
		$.each(data.users, function(i,item){
			$("#usersOrderedByPointsTBody").append("<tr id='" + item.userid + "'>" +
					"<td><a href=\"/adminconsole/users/edit?name=" + item.userid + "\">" + item.userid + "</a></td>" +
					"<td>" + item.points + "</td>" + 
                          "<td>" + 
                          "<button class='button button-gray' onclick='removeUser(\"" + item.userid + "\");'><span class='bin'></span>Delete</button>" +
                          "</td>" + 
                           "</tr>");
		});
	})
	pageNumber++;
	$("#getMoreByPoints").empty().append("<button class=\"button button-gray\" onclick=\"getMoreByPoints("+pageNumber+")\">See more</button>");
}
