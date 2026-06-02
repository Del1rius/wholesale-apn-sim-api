"""
Custom throttling classes for API rate limiting.
Provides granular control over different endpoint types.
"""

from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class BurstRateThrottle(UserRateThrottle):
    """
    Allows short bursts of requests (60 per minute).
    Useful for interactive API calls like viewing dashboards or lists.
    """
    scope = 'burst'
    
    def allow_request(self, request, view):
        # Bypass throttle for admins
        if request.user and request.user.is_authenticated:
            if request.user.is_superuser or getattr(request.user, 'role', None) == 'network_admin':
                return True
        return super().allow_request(request, view)


class SustainedRateThrottle(UserRateThrottle):
    """
    Long-term rate limit (2000 per day).
    Prevents sustained abuse over extended periods.
    """
    scope = 'sustained'
    
    def allow_request(self, request, view):
        # Bypass throttle for admins
        if request.user and request.user.is_authenticated:
            if request.user.is_superuser or getattr(request.user, 'role', None) == 'network_admin':
                return True
        return super().allow_request(request, view)


class UsageLoggingThrottle(UserRateThrottle):
    """
    High-frequency throttle for usage logging endpoint (500 per minute).
    Designed for edge routers and systems that POST usage data frequently.
    This is higher than burst rate to accommodate legitimate high-volume ingestion.
    """
    scope = 'usage_logging'
    
    def allow_request(self, request, view):
        # Bypass throttle for admins
        if request.user and request.user.is_authenticated:
            if request.user.is_superuser or getattr(request.user, 'role', None) == 'network_admin':
                return True
        return super().allow_request(request, view)


class AdminRateThrottle(UserRateThrottle):
    """
    Bypass throttle for superusers and network administrators.
    This class is redundant now that all throttle classes check for admin status.
    Kept for backwards compatibility.
    """
    def allow_request(self, request, view):
        # Superusers and network admins get unlimited access
        if request.user and request.user.is_authenticated:
            if request.user.is_superuser or getattr(request.user, 'role', None) == 'network_admin':
                return True
        
        # Everyone else goes through normal throttling
        return super().allow_request(request, view)
    
    def get_cache_key(self, request, view):
        # If user is admin, return None so no throttle cache is created
        if request.user and request.user.is_authenticated:
            if request.user.is_superuser or getattr(request.user, 'role', None) == 'network_admin':
                return None  # No cache key = no throttling
        
        return super().get_cache_key(request, view)
