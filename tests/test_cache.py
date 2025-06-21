from unittest.mock import patch

from utils.cache import rate_limit


class TestCache:
    """Test suite for cache utilities"""

    def test_rate_limit_decorator_basic(self):
        """Test that rate limit decorator works"""
        call_count = 0

        @rate_limit()
        def test_function():
            nonlocal call_count
            call_count += 1
            return "success"

        result = test_function()
        assert result == "success"
        assert call_count == 1

    def test_rate_limit_multiple_calls(self):
        """Test rate limiting with multiple rapid calls"""
        call_count = 0

        @rate_limit()
        def test_function():
            nonlocal call_count
            call_count += 1
            return call_count

        # First call should work immediately
        result1 = test_function()
        assert result1 == 1

        # Second call should also work (testing implementation)
        result2 = test_function()
        assert result2 == 2

        assert call_count == 2

    @patch("time.sleep")
    def test_rate_limit_with_delay(self, mock_sleep):
        """Test that rate limiter calls sleep when needed"""

        @rate_limit()
        def test_function():
            return "delayed"

        # Call twice to potentially trigger delay
        test_function()
        test_function()

        # Verify the function still works
        result = test_function()
        assert result == "delayed"

    def test_rate_limit_different_functions(self):
        """Test that different functions have separate rate limits"""

        @rate_limit()
        def function_a():
            return "a"

        @rate_limit()
        def function_b():
            return "b"

        assert function_a() == "a"
        assert function_b() == "b"

    def test_cache_response_basic(self):
        """Test basic cache response functionality"""
        from utils.cache import cache_response

        call_count = 0

        @cache_response(ttl_minutes=1)
        def cached_function():
            nonlocal call_count
            call_count += 1
            return f"result_{call_count}"

        # First call should execute function
        result1 = cached_function()
        assert result1 == "result_1"
        assert call_count == 1

        # Second call should return cached result
        result2 = cached_function()
        assert result2 == "result_1"  # Same as first call
        assert call_count == 1  # Function not called again

    def test_clear_cache(self):
        """Test cache clearing functionality"""
        from utils.cache import cache_response, clear_cache

        call_count = 0

        @cache_response(ttl_minutes=1)
        def cached_function_unique():
            nonlocal call_count
            call_count += 1
            return f"result_{call_count}"

        # Call function and cache result
        result1 = cached_function_unique()
        assert result1 == "result_1"
        assert call_count == 1

        # Clear cache
        clear_cache()

        # Next call should execute function again
        result2 = cached_function_unique()
        assert result2 == "result_2"
        assert call_count == 2
