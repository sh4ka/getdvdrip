$(document).ready(function(){

	if($.cookie("show_head_help") == null){
		$(".alert").alert();
		$(".alert").removeClass('hide');
	}

	$('.alert').bind('closed', function () {
	  $.cookie('show_head_help', 'false', { expires: 365 });
	})
})