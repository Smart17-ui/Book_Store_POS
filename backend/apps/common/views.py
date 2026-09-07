from django.http import JsonResponse


def api_root(request):
	return JsonResponse({
		'name': 'Bookstore POS API',
		'status': 'ok',
		'endpoints': {
			'api': '/api/',
			'admin': '/admin/',
		},
	})
