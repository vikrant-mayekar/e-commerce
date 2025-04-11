from django.middleware.common import CommonMiddleware

class CustomCommonMiddleware(CommonMiddleware):
    def process_response(self, request, response):
        response = super().process_response(request, response)
        if response.status_code == 404:
            # Add security headers for 404 responses
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-Frame-Options'] = 'SAMEORIGIN'
            response['X-XSS-Protection'] = '1; mode=block'
        return response 