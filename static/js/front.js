$(document).ready(function(){
	var search_url = 
	$('.release-magnet').click(function(e){
		e.preventDefault();
		selected_id = $(this).attr('data-id')
		$('.modal-release-title').html($(this).attr('data-title'));
		$('.modal-release-synopsis').html($(this).attr('data-synopsis'));
		get_magnet_links($(this).attr('data-title'));
		$('#modal_release').modal('toggle');
	})

	function get_magnet_links(title){
		title = escape(title);
		$.ajax({
			url : 'search_magnet.json',
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
