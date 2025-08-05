import time
import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse

logger = logging.getLogger(__name__)


class RequestMonitoringMiddleware(MiddlewareMixin):
    """
    Middleware to monitor request performance and log request details
    """
    
    def process_request(self, request):
        """Start timing the request"""
        request.start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """Log request details and timing"""
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # Log request details
            logger.info(
                f"Request: {request.method} {request.path} - "
                f"Status: {response.status_code} - "
                f"Duration: {duration:.3f}s"
            )
            
            # Add timing header to response
            response['X-Request-Duration'] = f"{duration:.3f}"
        
        return response
    
    def process_exception(self, request, exception):
        """Log exceptions"""
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            logger.error(
                f"Exception in {request.method} {request.path}: {exception} - "
                f"Duration: {duration:.3f}s"
            )
        return None


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """
    Middleware to monitor API performance and provide metrics
    """
    
    def process_request(self, request):
        """Initialize performance tracking"""
        request.performance_data = {
            'start_time': time.time(),
            'endpoints_called': []
        }
        return None
    
    def process_response(self, request, response):
        """Track API performance metrics"""
        if hasattr(request, 'performance_data'):
            duration = time.time() - request.performance_data['start_time']
            
            # Track slow requests
            if duration > 1.0:  # Log requests taking more than 1 second
                logger.warning(
                    f"Slow request detected: {request.method} {request.path} - "
                    f"Duration: {duration:.3f}s"
                )
            
            # Add performance headers
            response['X-Response-Time'] = f"{duration:.3f}"
            response['X-Performance-Monitored'] = 'true'
        
        return response
    
    def process_exception(self, request, exception):
        """Track performance for failed requests"""
        if hasattr(request, 'performance_data'):
            duration = time.time() - request.performance_data['start_time']
            logger.error(
                f"Performance issue: {request.method} {request.path} failed - "
                f"Duration: {duration:.3f}s - Error: {exception}"
            )
        return None 