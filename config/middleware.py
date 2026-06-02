"""
Custom middleware for logging and monitoring.
"""

import logging
import time
import json
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('api')


class APILoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all API requests and responses.
    Logs request method, path, user, response status, and duration.
    """
    
    def process_request(self, request):
        """Called before the view is executed"""
        request._start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """Called after the view is executed"""
        # Only log API requests (not static files or admin)
        if request.path.startswith('/api/'):
            duration = time.time() - getattr(request, '_start_time', time.time())
            
            # Get user info
            user = 'Anonymous'
            if hasattr(request, 'user') and request.user.is_authenticated:
                user = request.user.username
            
            # Get request body (for POST/PUT/PATCH)
            request_body = None
            if request.method in ['POST', 'PUT', 'PATCH']:
                try:
                    if hasattr(request, 'body'):
                        request_body = request.body.decode('utf-8')[:500]  # Limit to 500 chars
                except Exception:
                    request_body = '[Unable to decode body]'
            
            # Log the request
            log_data = {
                'method': request.method,
                'path': request.path,
                'user': user,
                'status_code': response.status_code,
                'duration_ms': round(duration * 1000, 2),
                'ip_address': self.get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', '')[:200],
            }
            
            if request_body:
                log_data['request_body'] = request_body
            
            # Log at different levels based on status code
            if response.status_code >= 500:
                logger.error(f"API Request Failed: {json.dumps(log_data)}")
            elif response.status_code >= 400:
                logger.warning(f"API Request Error: {json.dumps(log_data)}")
            else:
                logger.info(f"API Request: {json.dumps(log_data)}")
        
        return response
    
    def get_client_ip(self, request):
        """Get the client's IP address from the request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """
    Middleware to monitor slow requests and log performance warnings.
    """
    
    SLOW_REQUEST_THRESHOLD = 1.0  # seconds
    
    def process_request(self, request):
        """Called before the view is executed"""
        request._start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """Called after the view is executed"""
        duration = time.time() - getattr(request, '_start_time', time.time())
        
        # Log slow requests
        if duration > self.SLOW_REQUEST_THRESHOLD:
            logger = logging.getLogger('django.request')
            logger.warning(
                f"Slow request detected: {request.method} {request.path} "
                f"took {duration:.2f}s (threshold: {self.SLOW_REQUEST_THRESHOLD}s)"
            )
        
        return response
