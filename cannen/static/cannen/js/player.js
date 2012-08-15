// helper to refresh the info asynchronously
function refresh()
{
	$('#info').load('info',
					function()
					{
						// handle async links
						$('a.asynclink').click(
							function (event)
							{
								event.preventDefault();
								
								var anchor = $(this);
								$.get(anchor.attr('href'),
									  function (data)
									  {
										  refresh();
									  }
								);
							}
						);
						
						$("#sortable").sortable({
							axis: "y",
							cursor: "move",
							start: stop_info_refresh,
							stop: start_info_refresh,
							update: function() { saveQueue(); }
						});
						$("#sortable").disableSelection();
						loadQueue();
					}
				   );
}

// helpers for enabling / disabling refresh
var info_refresh = null;
function start_info_refresh()
{
	if (info_refresh == null)
	{
		refresh();
		info_refresh = setInterval(refresh, 2500);
	}
}
function stop_info_refresh()
{
	if (info_refresh != null)
	{
		clearInterval(info_refresh);
		info_refresh = null;
	}
}

$(document).ready(
	function (event)
	{
		// refresh info often
		start_info_refresh();
		
		// handle async forms ajax-like
		$('form.asyncform').submit(
			function (event)
			{
				event.preventDefault();
				
				var form = $(this);
				$.post(form.attr('action'), form.serialize(),
					   function (data)
					   {
						   refresh();
						   form.get(0).reset();
					   }
				);
			}
		);
		
		// set up the AJAX-ey file uploader
		$('#fileupload').fileupload(
			{
				dataType: 'txt',
				sequentialUploads: true,
				
				submit: function (e, data)
				{
					data.context = add_upload();
					if (data.context.name)
						data.context.name.text(data.files[0].name);
					if (data.context.status)
						data.context.status.text('queued');
					return true;
				},
				send: function (e, data)
				{
					if (data.context.status)
						data.context.status.text('0%');
				},
				progress: function (e, data)
				{
					var progress = parseInt(data.loaded / data.total * 100, 10);
					if (data.context.progress)
						data.context.progress.animate({width: progress + '%'});
					if (data.context.status)
						data.context.status.text(progress + '%');
				},
				always: function (e, data)
				{
					if (data.context.status)
						data.context.status.text('done');
					if (data.context.main)
						data.context.main.fadeOut(1000, function() { $(this).remove(); });
					refresh();
				},
			}
		);
		
		// since we have javascript, hide the submit button for files
		$("#fileuploadsubmit").remove();
	}
);
