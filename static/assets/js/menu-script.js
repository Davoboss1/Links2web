( function( $ ) {
$( document ).ready(function() {
	
	$("#cssmenu li.has-sub>a").attr("style","display:flex; padding-left:0; text-indent:20px;");
	$("#cssmenu li.has-sub>a").append("<span class='now-ui-icons arrows-1_minimal-down' style='margin-left:auto; '></span>");
	
$('#cssmenu li.has-sub>a').on('click', function(){
	
		$(this).removeAttr('href');
		var element = $(this).parent('li');
		if (element.hasClass('open')) {
			element.removeClass('open');
			element.find('li').removeClass('open');
			element.find('ul').slideUp();
		}
		else {
			element.addClass('open');
			element.children('ul').slideDown();
			//element.siblings('li').children('ul').slideUp();
			//element.siblings('li').removeClass('open');
			//element.siblings('li').find('li').removeClass('open');
//			element.siblings('li').find('ul').slideUp();
		}
	});
});
} )( jQuery );