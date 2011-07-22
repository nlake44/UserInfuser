var g_current_tab = "";
/* Counter code christianhellsten@github*/
(function($){  
  /**
   * Returns the current value of the counter.
   */
  function value(counter) {
    if (isNaN(counter.val())){
      return 0;
    }
    return parseInt(counter.val(), 10);
  }
  /**
   * Changes the counter's value.
   */
  function change(counters, step) {
    return counters.each(function() {  
      var $counter = $(this);
      // Increment counter
      var count = value($counter) + step;
      $counter.val(count);
      // Trigger event
      var event_name = step > 0 ? 'increment' : 'decrement';
      $counter.trigger(event_name, [$counter, count]);
      return count;
    });  
  }
  $.fn.increment = function(step) {  
    if(!step) { step = 1; }
    change(this, step);
  };  
  $.fn.decrement = function(step) {  
    if(!step) { step = -1; }
    change(this, step);
  };  
  $.fn.counterValue = function() {  
    return value($(this));
  };  
})(jQuery); 

function callback(){
}
function callback2(data){
}
function trashTask(tag){
  var taskid = tag;
  //strip down to just the taskid
  var server_response = function(data){
    if (data.success !== "true"){
      alert("There was an error in your request: "+data.error); 
      return;
    }
    else{
      // Successful addition
      $("#"+tag).effect("blind", {}, 0, callback);
      $("#"+tag).fadeOut(function(){
        $("#"+taskid).remove();
      });
    }
  };
  // Serverside request
  $.post("/updatetask", {'name':"name",
                         'tid':taskid,
                         'content':"content", 
                         'state':'delete'}, 
          server_response, "json");
}

//Same as above, but with a jquery item
function dropTrashTask($item){
  var taskid = $item.attr("id");
  trashTask(taskid);
}

function checkoffTask(tag){
  var taskid = tag;
  //strip down to just the taskid
  var server_response = function(data){
    if (data.success !== "true"){
      alert("There was an error in your request: "+data.error); 
      return;
    }
    else{
      // Successful response
      //$("#points-"+data.pid).effect("fade", {}, 1000, callback);
      $("#points-"+data.pid).effect("fade", {}, 1000, callback);
      $("#points-"+data.pid).fadeOut();
      $("#points-"+data.pid).html("Points: "+data.prjpoints);
      $("#points-"+data.pid).fadeIn();
      $("#"+tag).effect("puff", {}, 500, callback);
      $("#"+tag).fadeOut(function(){
        $("#"+tag).fadeIn();
      });
    }
  };
  // Serverside request
  $.post("/updatetask", {'name':'name',
                         'tid':taskid,
                         'content':'content',
                         'state':'complete'}, 
                         server_response, 
                         "json");
}

function dropCheckoffTask($item){
  var taskid = $item.attr("id");
  checkoffTask(taskid);
}

function setup_notification_dialog(){
    var confirmed = function(){
      $("#notification-dialog").dialog("close");
    };

    var dialogOpts = {
      autoOpen: false,
      draggable: false,
      show: 'puff',
      hide: 'fold',
      position: 'center',
      modal: true,
      buttons: {
        "Close": confirmed
      }
    };

    $("#notification-dialog").dialog(dialogOpts);
}

function notify(message, title){
  $("#notification").remove();
  msg = $("<div>").append(message).attr("id","notification");
  $("#notification-dialog").append(msg);
  if (title){
    $("#ui-dialog-title-notification-dialog").html(title);
  }
  else{
    $("#ui-dialog-title-notification-dialog").html("Notification Message");
  }
  $("#notification-dialog").dialog("open");
}

function shakeIt(tag){
  $("#" + tag).effect("shake", {times:2}, 300, callback);
}

function updateFieldCallback(value, settings){
  console.log(value);
  console.log(this.id);
}

function appendTask(tasktag, name, tabtag, content, points){
  // curtask is the block that holds points, task, and task buttons  
  var curtask = $("<span>");
  curtask.attr("id",tasktag);
  curtask.addClass("taskholder"); 
  // points holder holds up arrow, points, and down arrow
  var points_holder = $("<span>")
  points_holder.addClass("pointsblock");
  // A task holds the name and details
  var task = $("<span>").addClass("task");
 
  var points_div = $("<span>").html(points);
  points_div.attr("id","points-" + tasktag);

  points_div.editable("/updatefield",
                      {indicator: "Saving...",
                      tooltip: "Click to edit",
                      indicator : '<img src="/static/images/indicator.gif">',
                      submit: "Save",
                      cancel: "Cancel",
                      type: 'textarea',
                      callback: updateFieldCallback});

  var arrowup = $("<div>").addClass("uparrow");
  
  arrowup.click(function(){
    var p = points_div.html();
    p = parseInt(p, 10);
    p = p + 1;
    points_div.html(p);
    $.post("/updatefield", {'id':points_div.attr("id"),
                        'value':points_div.html()},
                         callback2, "json");
   });
  var arrowdown = $("<div>").addClass("downarrow");
  arrowdown.click(function(){
    var p = points_div.html();
    p = parseInt(p, 10);
    p = p - 1;
    points_div.html(p);
    $.post("/updatefield", {'id':points_div.attr("id"),
                        'value':points_div.html()},
                         callback2, "json");
   });

  points_holder.append(arrowup);
  points_holder.append(points_div);
  points_holder.append(arrowdown);
  curtask.append(points_holder); 

  var details = $("<div>").html(content);
  details.addClass("ui-widget-content ui-state-default ui-corner-all taskdetails");
  details.attr("id","details-" + tasktag)
  details.editable("/updatefield",
                      {indicator: "Saving...",
                      tooltip: "Click to edit",
                      submit: "Save",
                      cancel: "Cancel",
                      indicator : '<img src="/static/images/indicator.gif">',
                      type: 'textarea',
                      callback: updateFieldCallback});

  var newname = $("<div>").html(name);
  newname.addClass("ui-widget ui-widget-header ui-corner-all taskname");
  //newname.addClass("ui-widget ui-widget-header ui-corner-all ui-draggable taskname");
  newname.attr("id","name-" + tasktag);
  newname.editable("/updatefield",
                      {indicator: "Saving...",
                      tooltip: "Click to edit",
                      submit: "Save",
                      cancel: "Cancel",
                      indicator : '<img src="/static/images/indicator.gif">',
                      type: 'textarea',
                      callback: updateFieldCallback});
   if (points < 0){
    details.css('background','orange');
  }
  task.append(newname);
  task.append(details);

  curtask.append(task);
  curtask.hide().fadeIn(1000);
  /*
  curtask.draggable({cancel: "a.ui-icon",
                     revert: "invalid",
                     helper: function( event){
                       return $("<div class='ui-widget-header'>Move Task</div>");
                     },
                     cursorAt: {top: 0, left: 0},
                     cursor: "move"});
  */
  // Buttons on hover
  var buttonset = $("<span>").attr("id","task-button-set");
  buttonset.addClass("taskbuttons");
  buttonset.buttonset();

  var trashbutton = $("<a>").attr("href","javascript:trashTask(\"" + tasktag + "\")");
  trashbutton.attr("title",'trash it');
  trashbutton.addClass('ui-button ui-icon ui-icon-trash');
  trashbutton.attr("id","hovertrashbutton");

  var spacer1 = $("<span>").html("|");

  var completedbutton = $("<a>").attr("href","javascript:checkoffTask(\""+ tasktag+ "\")");
  completedbutton.attr("title","completed");
  completedbutton.addClass("ui-button ui-icon ui-icon-check");
  completedbutton.attr("id","hovercompletedbutton");

  buttonset.append(completedbutton);
  buttonset.append(spacer1);
  buttonset.append(trashbutton);

  curtask.hover(
    function(){
      $(this).append(buttonset);
    }, 
    function(){
      $("#task-button-set").remove();
    }
  );

  $("#"+tabtag).append(curtask);

}
function notifyServerAppendTask(){
  console.info("added task");  
}
function plusTaskButton(){
  $("#plus-task-button").remove();
  var plus = $("<img>").attr("src","/static/images/add-task2-nohover.png");
  plus.attr("style","height:30px; padding-left:240px;");
  plus.attr("id","plus-task-button");
  plus.hover(function(){
    plus.attr("src","/static/images/add-task2.png");
  },
  function(){
    plus.attr("src","/static/images/add-task2-nohover.png");
  });
  plus.click(function(){
    // this should put in a empty task to be edited
    //loadTaskDialog();
    $("#plus-task-button").remove();
    appendTask("newtaskid",
               "click here to edit me", 
               g_current_tab,
               "click here to edit me", 
               0);
    plusTaskButton();
    notifyServerAppendTask();
  });
  // Only put the plus on certain tabs, not these ones
  if(g_current_tab != "ptab-___removeproject" &&
     g_current_tab != "ptab-__newproject"){
    $("#"+g_current_tab).append(plus);
    $("#"+g_current_tab).append(plus);
  }
}
//Add task
function setup_new_task_dialog(){
  var cancel = function(){
    $("#add-task-dialog").dialog("close");
  };
  var confirmed = function(){
    var name = $("#new-task-name").val();
    var prjname = $("#new-task-project-select :selected").text();
    var content = $("#new-task-summary").val();
    var points = $("#new-task-points").val();

    if(name.length === 0){
      shakeIt("new-task-name"); 
      return;
    }
    if (isNaN(points)){
      shakeIt("new-task-points");
      notify("The number of points must be a number","Error");
      return;
    }
    // The response function from the ajax call
    var server_response = function(data){
      if (data.success !== "true"){
        alert("There was an error in your request: "+data.error); 
        return;
      } 
      var tid = data.tid;
      var newname = name ; //+ " ("+data.points+")" ;
      //Put focus on this new task
      $("#project-tabs").tabs("select","#ptab-"+data.pid);

      appendTask(tid, newname, "ptab-" + data.pid, content, points);

      $("plus-task-button").remove();
      $("#add-task-dialog").dialog("close");
      //plusTaskButton();
    };
    $.post("/newtask", {'name':name,
                        'projectname':prjname,
                        'content':content,
                        'state':'active',
                        'points':points}, 
                         server_response, "json");
  };

  var dialogOpts = {
      height:300,
      width:300,
      stack: true,
      autoOpen: false,
      draggable: false,
      //show: 'puff',
      hide: 'fold',
      position: "center",
      modal: true,
      buttons: {
        "OK": confirmed,
        "Cancel":cancel
      }
  };
  $("#add-task-dialog").dialog(dialogOpts);
}

function setup_new_project(){
  var name = $("#new-project-name").val();
  var content = $("#new-project-summary").val();
  if(name.length === 0){
    shakeIt("new-project-name"); 
    return;
  }
  // The response function from the ajax call
  var server_response = function(data){
    if (data.success !== "true"){
      alert("There was an error in your request: "+data.error); 
      return;
    } 
    var pid = data.pid;
    var curprojdiv = $("<div>").attr("id","ptab-" + pid);
    var curprojlist = $("<li>").attr("id","plist-" + pid);
    var listlink = $("<a>").attr("href","#ptab-" + pid);
    var listspan = $("<span>").html(name);

    var prjheader = $("<div>");
    prjheader.addClass("project-header");
    var prjname = $("<span>").html(name);
    var prjpoints = $("<span>").html("Points: 0");
    prjpoints.attr("id","points-"+pid);
    prjpoints.attr("style","float:right;");
    prjheader.append(prjname);
    prjheader.append(prjpoints);
    prjheader.append($("<hr>"));
    curprojdiv.append(prjheader);
    curprojdiv.addClass("ui-tabs-panel ui-widget-content ui-corner-bottom ui-tabs-hide");

    projpoints = $("<span>").attr("style","float:right");
    curprojdiv.append(projpoints);

    listlink.append(listspan); 
    curprojlist.append(listlink);  
    curprojlist.addClass("ui-state-default ui-corner-top");
    
    curprojlist.hide().fadeIn(0);
    curprojdiv.hide().fadeIn(0);
    $("#newproject-list-item").before(curprojlist);
    $("#ptab-__newproject").before(curprojdiv);
    $("#project-tabs").tabs("destroy");
    $("#project-tabs").tabs({ collapsible: false, 
                              spinner:"Updating..."});
    $("#project-tabs").tabs("select","#ptab-" + pid);
  };    
  $.post("/newproject", {'name':name,
                         'content':content,
                         'state':'active'}, 
                         server_response, "json");
}

function loadProjectsForRemove(){
  $.get("/getprojects", function(response){
    // EVAL IS EVIL
    var data = eval('(' + response + ')');
    if(data.success == "false"){
      alert("Error loading projects: " + data.error); 
      return;
    }
    $("#remove-project-select").remove();
    if (data.projects.length == 2){
      // There are no projects to remove  
      var warning = $("<div>").html("There are no projects to remove");
      warning.attr("id","remove-project-select");
      $("#remove-project-select-holder").append(warning);
      $("#remove-project-button").hide();
    }
    else{
      $("#remove-project-button").fadeIn();
      var select = $("<select>").attr("id","remove-project-select");
      $("#remove-project-select-holder").append(select);
      $("#remove-project-select").select();
      $("#remove-project-select").addOption(eval('(' + data.projects + ')'), true);
    } 
  });
}

function loadTaskDialog(){
  $("#new-task-name").val("");
  $("#new-task-summary").val("");
  $("#new-task-points").val(1);
  $("#add-task-dialog").dialog("open");
  //$("#new-task-project-select").addOption("Loading...":"loading...");
  $.get("/getprojects", function(response){
    // EVAL IS EVIL
    var data = eval('(' + response + ')');
    if(data.success == "false"){
      alert("Error loading projects: " + data.error); 
      return;
    }
    if (data.projects.length == 2){
      notify("Create a project first!","First things first");
      $("#add-task-dialog").dialog("close");
      return;
    }
    $("#new-task-project-select").empty();
    $("#new-task-project-select").addOption(eval('(' + data.projects + ')'), false);
    if (g_current_tab !== ""){
      var project_id = g_current_tab.substring(5);
      $("#new-task-project-select").val(project_id);
    }
  });
}



function setupTabs(intropid){
  $("#project-tabs").tabs({ collapsible: false, 
                            spinner: "Updating..."});
  $("#project-tabs").bind("tabsselect",function(event,ui){
    if(ui.panel.id == "ptab-___removeproject"){
      loadProjectsForRemove();
    }
    g_current_tab = ui.panel.id;
    //plusTaskButton();
  });
  // Where does the focus go
  if (intropid !== ""){
    $("#project-tabs").tabs("select","ptab-"+intropid);
  }
}
function set_projects(proj){
  var intropid = "";
  // loop through projects, attach them to the list
  if (proj === undefined){
    setupTabs(intropid);
    return;
  }
  for (var ii = 0; ii < proj.length; ii++){
    var curprojdiv = $("<div>").attr("id","ptab-" + proj[ii].pid);
    var curprojlist = $("<li>").attr("id","plist-" + proj[ii].pid);
    var listlink = $("<a>").attr("href","#ptab-" + proj[ii].pid);
    var listspan = $("<span>").html(proj[ii].name);
    //curprojdiv.html("<h1>" + proj[ii].name + "</h1>");
    curprojdiv.addClass("ui-tabs-panel ui-widget-content ui-corner-bottom ui-tabs-hide");
    var prjheader = $("<div>");
    prjheader.addClass("project-header");
    var prjname = $("<span>").html(proj[ii].name);
    var prjpoints = $("<span>").html("Points: " + proj[ii].points);
    prjpoints.attr("id","points-"+proj[ii].pid);
    prjpoints.attr("style","float:right;");
    prjheader.append(prjname);
    prjheader.append(prjpoints);
    prjheader.append($("<hr>"));
    curprojdiv.append(prjheader);
    curprojdiv.addClass("ui-tabs-panel ui-widget-content ui-corner-bottom ui-tabs-hide");

    curprojlist.append(listlink);
    curprojlist.addClass("ui-state-default ui-corner-top");
    listlink.append(listspan); 
    $("#newproject-list-item").before(curprojlist);
    $("#ptab-__newproject").before(curprojdiv);
    if (proj[ii].name == "Intro"){
      intropid = proj[ii].pid;
    }  
  }
  setupTabs(intropid);
}

function set_tasks(tasks){
  // Add to Project Tab
  if (tasks === undefined){
    return ;
  }
  for (var ii = 0; ii < tasks.length; ii++){
    appendTask(tasks[ii].tid, 
               tasks[ii].name, //+ " (" + tasks[ii].points + ")", 
               "ptab-"+tasks[ii].pid,
               tasks[ii].content, 
               tasks[ii].points);
  }
}

function got_user_info(info){
  //EVAL IS EVIL
  var json_info = eval('(' + info + ')');
  $("#myaccount-email").html(json_info.email);
  set_projects(json_info.projects);
  set_tasks(json_info.tasks);
  //plusTaskButton();
}

function show_actions(){
  notify("Actions","Actions");
}
function show_rewards(){
  notify("Rewards","Rewards");
}
function show_stats(){
  notify("Stats","Stats");
}
function show_sharing(){
  notify("Share","Share");
}
function show_goals(){
  notify("Goals","Goals");
}

function onPageLoad(){
  $(document).ready(function(){
  //hide toolbar and make visible the 'show' button
    $("span.downarr a").click(function() {
      $("#toolbar").slideToggle("fast");
      $("#toolbarbut").fadeIn("slow");
    });

    //show toolbar and hide the 'show' button
    $("span.showbar a").click(function() {
      $("#toolbar").slideToggle("fast");
      $("#toolbarbut").fadeOut();
    });
   //show tooltip when the mouse is moved over a list element 
    $("ul#social li").hover(function() {
      $(this).find("div").fadeIn("fast").show(); //add 'show()'' for IE
      $(this).mouseleave(function () { //hide tooltip when the mouse moves off of the element
        $(this).find("div").hide();
      });
    });
    //show quick menu on click
    $("span.menu_title a").click(function() {
      if($(".quickmenu").is(':hidden')){ //if quick menu isn't visible
        $(".quickmenu").fadeIn("fast"); //show menu on click
      }
      else if ($(".quickmenu").is(':visible')) { //if quick menu is visible
        $(".quickmenu").fadeOut("fast"); //hide menu on click
      }
    });

    //hide menu on casual click on the page
    $(document).click(function() {
        $(".quickmenu").fadeOut("fast");
    });
    $('.quickmenu').click(function(event) {
      event.stopPropagation(); //use .stopPropagation() method to avoid the closing of quick menu panel clicking on its elements
    });

    //don't jump to #id link anchor
    $(".facebook, .twitter, .delicious, .digg, .rss, .stumble, .menutit, span.downarr a, span.showbar a").click(function() {
   return false;
    });

  });
}

function init_myaccount(){
  $("#project-tabs").tabs({ collapsible: false, 
                            spinner:"Updating..."});
  setup_new_task_dialog();
  setup_notification_dialog();
  // Droppable Items
  /*
  $("#checkbox-drop").droppable({
                                 activeClass: "ui-state-highlight",
                                 drop: function(event, ui){
                                     dropCheckoffTask(ui.draggable);
                                  }
                                });
  $("#trash-drop").droppable({
                                 activeClass: "ui-state-highlight",
                                 drop: function(event, ui){
                                     dropTrashTask(ui.draggable);
                                   }
                                });
  */ 
  $("#add-project-button").click(function(){
    $("#add-project-button").removeClass("ui-state-focus");
    setup_new_project();
  });

  $("remove-project-button").button();
  $("#remove-project-button").click(function(){
    $("#remove-project-button").removeClass("ui-state-focus");
    var server_response = function(data){
      if (data.success !== "true"){
        alert("There was an error in your request: "+data.error); 
        return;
      }
      else{
        var tasks = data.tasks;
        $("#plist-"+data.pid).slideToggle('slow', function(){
          $("#plist-"+data.pid).remove();
        });
        $("#ptab-"+data.pid).slideToggle('slow', function(){
          $("#ptab-"+data.pid).remove();
        });
        $("#project-tabs").tabs("destroy");
        $("#project-tabs").tabs({ collapsible: false, 
                                  spinner:"Updating..."});
      }
    };
    var prjname = $("#remove-project-select :selected").text();
    $.post("/updateproject", {'name':prjname,'state':'delete'}, 
                             server_response, "json");
  });
  $("#add-task-button").button();
  $("#add-task-button").click(function(){
    $("#add-task-button").removeClass("ui-state-focus");
    // This opens the dialog on completion
    loadTaskDialog();
  });
 
  $.get("/getaccount",got_user_info);
  onPageLoad();
}
