$(document).ready(function(){
	
	$('.release-magnet').click(function(e){
		e.preventDefault();
		$('#magnet-links-list').html('<li><img src="/static/img/ajax-loader.gif" alt="loading..." /></li>')
		selected_id = $(this).attr('data-id')
		$('.modal-release-title').html($(this).attr('data-title'));
		$('.modal-release-synopsis').html($(this).attr('data-synopsis'));
		if($(this).attr('data-crating') == '-1'){
			crating = 'N/A'
		}
		else{
			crating = $(this).attr('data-crating');
		}
		$('.modal-release-crating').html(crating);
		$('.modal-release-arating').html($(this).attr('data-arating'));
		get_magnet_links($(this).attr('data-title'));
		$('#modal_release').modal('toggle');
	})

	$('.movie-permalink').click(function(e){
		e.preventDefault();
		window.location = '/search/'+encodeURI($(this).html());
	})

	function get_magnet_links(title){
		//title = title.replace(' ', '-');
		$.ajax({
			url : '/search_magnet.json',
			dataType: 'json',
			data :  {
				search: title
			},
			cache: true,
			success : function( response )
			{
				set_magnet_links(response)
			}
		});
	}

	function set_magnet_links(link_list){		
		list_links = ''
		$.each(link_list, function(key, value){
			// name, link, comments, uploader, u date, size, cat, subcat, seeders, leechers, trusted
			li = '<li><a href="'+value.magnet+'">'+value.name+'</a></li>'
			list_links += li
		})
		$('#magnet-links-list').html(list_links)
	}
})
