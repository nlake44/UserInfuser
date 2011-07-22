$(document).ready(function(){
    $('.button').mousedown(function(){
        $(this).addClass('active');
    }).bind('mouseup mouseout', function(){
        $(this).removeClass('active');
    });
});


$(function() {
    $('table').attr('cellpadding', 0).attr('cellspacing', 0).attr('border', 0);
    $('header, header li, header a, #promo, footer, #wrapper > section > div > aside nav > ul > li a, #wrapper > section > div > aside nav.global > ul > li > a span, .main-section, .main-content, .main-content > header, .main-content > header .help, .main-content > section, .preview-pane .preview, .listing li, .pagination a, input, button, .button, .button span, textarea, select, .message, .message-close, #calroot, #calhead, #calbody, .progress, .progress > span, ul.tabs > li > a, ul.tabs > li, ul.tabs, .panes section, .panes, table.datatable thead th, table.datatable tr, table.datatable td, table.datatable').each(function() {
        PIE.attach(this);
    });
});
