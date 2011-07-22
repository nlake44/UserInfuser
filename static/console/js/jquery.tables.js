(function($){  
    $.fn.paginate = (function(options) {

        var defaults = {
            rows: 20,
            buttonClass: 'blue-button',
            effect: 'default'
        };
        var options = $.extend(defaults, options);
  
        return this.each(function() {
            var trs = $(this).find('tbody tr');
            var pages = $('<ul class="pagination clearfix"></ul>');
            if (!$(this).hasClass('paginate')) $(this).addClass('paginate');
            for(var i = 0; i < trs.length; i+=options.rows) {
                trs.slice(i, i+options.rows).wrapAll("<tbody></tbody>");
                pages.append('<li class="page"><a class="'+options.buttonClass+'" href="#">'+(i/options.rows+1)+'</a></li>');
            }
            var api = $(this).find("tbody > tbody").unwrap().parents('table.paginate').after(pages).next().tabs("table.paginate > tbody", {effect: options.effect}).data("tabs");
            $('<li class="prev"><a class="'+options.buttonClass+'" href="#">&laquo;</a></li>').click(function(){
                if (api.getIndex()>0) api.prev(); return false;
            }).prependTo(pages);
            $('<li class="first"><a class="'+options.buttonClass+'" href="#">First</a></li>').click(function(){
                api.click(0); return false;
            }).prependTo(pages);
            $('<li class="next"><a class="'+options.buttonClass+'" href="#">&raquo;</a></li>').click(function(){
                if (api.getIndex()<trs.length/options.rows) api.next(); return false;
            }).appendTo(pages);
            $('<li class="last"><a class="'+options.buttonClass+'" href="#">Last</a></li>').click(function(){
                api.click(trs.length/options.rows-1); return false;
            }).appendTo(pages);
            return $(this);
        });  
    });

    $.fn.sortElements = (function(){

        var sort = [].sort;
 
        return function(comparator, getSortable) {
 
            getSortable = getSortable || function(){return this;};
 
            var placements = this.map(function(){
 
                var sortElement = getSortable.call(this),
                    parentNode = sortElement.parentNode,
 
                // Since the element itself will change position, we have
                // to have some way of storing its original position in
                // the DOM. The easiest way is to have a 'flag' node:
                nextSibling = parentNode.insertBefore(
                    document.createTextNode(''),
                    sortElement.nextSibling
                );
 
                return function() {
 
                    if (parentNode === this) {
                        throw new Error(
                            "You can't sort elements if any one is a descendant of another."
                        );
                    }
 
                    // Insert before flag:
                    parentNode.insertBefore(this, nextSibling);
                    // Remove flag:
                    parentNode.removeChild(nextSibling);
 
                };
 
            });
 
            return sort.call(this, comparator).each(function(i){
                placements[i].call(getSortable.call(this));
            });
 
        };
 
    })();

    $.fn.tablesort = (function(options) {
        return this.each(function() {  
            var table = $(this);
            $(this).find('thead th').wrapInner('<a href="#"/>').find('a').click(function(){
              var sort = $(this).data('sort');
              $(this).parents('thead').find('a').removeClass('sort-asc sort-desc');
              sort = (sort=='asc'? 'desc' : (sort=='desc'? 'asc' : 'asc'));
              $(this).data('sort', sort).addClass('sort-'+sort);
              table.find('tbody tr td').removeClass('column-selected');
              table.find('tbody tr td:nth-child('+($(this).parent().index()+1)+')').sortElements(
                function(a, b){
                    return sort=='desc'? ($(a).text() < $(b).text()) - ($(a).text() > $(b).text()) : ($(a).text() > $(b).text()) - ($(a).text() < $(b).text());
                },
                function(){
                    return this.parentNode; 
                }
              ).addClass('column-selected');
              return false;
            });
            return $(this);
        });
    });

})(jQuery);

jQuery(document).ready(function(){
    jQuery("table.paginate").paginate({rows: 10, buttonClass: 'button-blue'});

    jQuery("table.sortable").tablesort();

    jQuery("table.selectable tbody tr").hover(
        function() {$(this).addClass('hover');},
        function() {$(this).removeClass('hover');}
    ).click(function(){
        $(this).siblings().removeClass('selected');
        $(this).toggleClass('selected');
    });
});

function allCheck(table, value){
	if (value == true){
		$(table).find('tbody tr:visible td:first-child input[type=checkbox]').attr('checked', 'checked');
	}else {
		$(table).find('tbody tr:visible td:first-child input[type=checkbox]').removeAttr('checked');
	}
}
function indCheck(table,value){
	if (value == false){
		$(table).find('.checkall').removeAttr('checked');
	}else{
		if ($(table).find('tbody tr:visible td:first-child input[type=checkbox]:not(:checked)').length) {
			$(table).find('.checkall').removeAttr('checked');
		}else {
			$(table).find('.checkall').attr('checked', 'checked');
		}
	}
}