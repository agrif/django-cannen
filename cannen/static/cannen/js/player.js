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

					}
	);
}

$(document).ready(
	function (event)
	{
		refresh();
		var auto_refresh = setInterval(refresh, 2500); // every 2.5 seconds
		
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
	}
);
