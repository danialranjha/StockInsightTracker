import functools
import time
from datetime import datetime, timedelta
import threading
from typing import Dict, Any

# Cache to store API responses
_cache: Dict[str, Dict[str, Any]] = {}
_cache_lock = threading.Lock()

# Rate limiting variables
_last_request_time = 0
_request_lock = threading.Lock()
MIN_REQUEST_INTERVAL = 2  # Minimum time between requests in seconds

def rate_limit():
    """Rate limiting decorator to prevent too many requests."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            global _last_request_time
            
            with _request_lock:
                current_time = time.time()
                time_since_last_request = current_time - _last_request_time
                
                if time_since_last_request < MIN_REQUEST_INTERVAL:
                    time.sleep(MIN_REQUEST_INTERVAL - time_since_last_request)
                
                _last_request_time = time.time()
                return func(*args, **kwargs)
        return wrapper
    return decorator

def cache_response(ttl_minutes: int = 15):
    """Cache decorator with Time-To-Live (TTL) in minutes."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create a cache key from function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            with _cache_lock:
                # Check if we have a valid cached response
                if cache_key in _cache:
                    cached_item = _cache[cache_key]
                    if datetime.now() < cached_item['expiry']:
                        print(f"Cache hit for {cache_key}")
                        return cached_item['data']
                    else:
                        print(f"Cache expired for {cache_key}")
                        del _cache[cache_key]
                
                # If no valid cache, call the function
                result = func(*args, **kwargs)
                
                # Cache the result with expiration time
                expiry = datetime.now() + timedelta(minutes=ttl_minutes)
                _cache[cache_key] = {
                    'data': result,
                    'expiry': expiry
                }
                print(f"Cached response for {cache_key}")
                return result
                
        return wrapper
    return decorator

def clear_cache():
    """Clear all cached responses."""
    with _cache_lock:
        _cache.clear()
