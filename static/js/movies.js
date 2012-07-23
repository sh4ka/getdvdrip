$(document).ready(function(){
	if($('#movie-title').html() != ''){
		get_magnet_links($('#movie-title').html())
	}

	function get_magnet_links(title){
		title = title.replace(' ', '-');
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