"""Integration tests for Vercel serverless function endpoints."""

import json
import io
from http.server import BaseHTTPRequestHandler
from unittest.mock import patch, MagicMock
import pytest


class MockHTTPRequest:
    """Mock HTTP request for testing Vercel handlers."""
    
    def __init__(self, method='GET', path='/', query_params=None):
        self.method = method
        self.path = path
        self.query_params = query_params or {}
        self.qs = query_params or {}


class MockHTTPResponse:
    """Mock HTTP response for testing Vercel handlers."""
    
    def __init__(self):
        self.status_code = None
        self.headers = {}
        self.body = io.BytesIO()
    
    def send_response(self, code):
        self.status_code = code
    
    def send_header(self, name, value):
        self.headers[name] = value
    
    def end_headers(self):
        pass
    
    def wfile_write(self, data):
        self.body.write(data)
    
    def get_body(self):
        return self.body.getvalue()


class TestVercelFundingRatesHandler:
    """Test Vercel funding rates serverless function."""

    @pytest.fixture(autouse=True)
    def reset_vercel_cache(self):
        """Reset Vercel cache before each test."""
        try:
            # Import here to avoid module import issues
            import sys
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../api'))
            
            import funding_rates as funding_rates_module
            funding_rates_module._cache = {
                'data': [],
                'last_update': None
            }
        except ImportError:
            pass

    @pytest.mark.integration
    @patch('api.funding_rates.fetch_all_funding_rates')
    @patch('api.funding_rates.combine_funding_data')
    def test_funding_rates_handler_success(self, mock_combine, mock_fetch):
        """Test successful funding rates handler execution."""
        # Import the handler
        from api.funding_rates import handler
        
        # Mock data
        mock_dex_data = {
            'dydx': {'BTC': 87.6, 'ETH': 43.8},
            'hyperliquid': {'BTC': 70.08, 'ETH': 35.04}
        }
        mock_combined_data = [
            {
                'market': 'BTC-USD',
                'dexRates': [
                    {'dex': 'dYdX', 'rate': 87.6},
                    {'dex': 'Hyperliquid', 'rate': 70.08}
                ],
                'volume24h': 0,
                'openInterest': 0,
                'lastUpdate': '2022-01-01T12:00:00'
            }
        ]
        
        mock_fetch.return_value = mock_dex_data
        mock_combine.return_value = mock_combined_data
        
        # Create mock request/response
        mock_response = MockHTTPResponse()
        
        # Create handler instance
        handler_instance = handler()
        handler_instance.send_response = mock_response.send_response
        handler_instance.send_header = mock_response.send_header
        handler_instance.end_headers = mock_response.end_headers
        handler_instance.wfile = MagicMock()
        
        with patch('time.time', return_value=1640995200.0):
            handler_instance.do_GET()
        
        # Verify response
        assert mock_response.status_code == 200
        assert mock_response.headers['Content-type'] == 'application/json'
        assert mock_response.headers['Access-Control-Allow-Origin'] == '*'
        
        # Verify the written data
        written_calls = handler_instance.wfile.write.call_args_list
        assert len(written_calls) == 1
        
        response_data = json.loads(written_calls[0][0][0].decode())
        assert 'data' in response_data
        assert 'lastUpdate' in response_data
        assert 'totalMarkets' in response_data
        assert len(response_data['data']) == 1

    @pytest.mark.integration
    def test_funding_rates_handler_cached_data(self):
        """Test funding rates handler with cached data."""
        from api.funding_rates import handler
        import api.funding_rates as funding_rates_module
        
        # Set up cached data
        cached_data = [
            {
                'market': 'ETH-USD',
                'dexRates': [
                    {'dex': 'dYdX', 'rate': 43.8},
                    {'dex': 'Hyperliquid', 'rate': 35.04}
                ],
                'volume24h': 0,
                'openInterest': 0,
                'lastUpdate': '2022-01-01T12:00:00'
            }
        ]
        
        funding_rates_module._cache = {
            'data': cached_data,
            'last_update': 1640995200.0
        }
        
        # Create mock response
        mock_response = MockHTTPResponse()
        
        # Create handler instance
        handler_instance = handler()
        handler_instance.send_response = mock_response.send_response
        handler_instance.send_header = mock_response.send_header
        handler_instance.end_headers = mock_response.end_headers
        handler_instance.wfile = MagicMock()
        
        # Call within cache duration
        with patch('time.time', return_value=1640995400.0):  # 200 seconds later (within 600s cache)
            handler_instance.do_GET()
        
        # Should use cached data without fetching
        written_calls = handler_instance.wfile.write.call_args_list
        response_data = json.loads(written_calls[0][0][0].decode())
        
        assert response_data['data'] == cached_data
        assert response_data['totalMarkets'] == 1

    @pytest.mark.integration
    @patch('api.funding_rates.fetch_all_funding_rates')
    def test_funding_rates_handler_cache_expired(self, mock_fetch):
        """Test funding rates handler with expired cache."""
        from api.funding_rates import handler
        import api.funding_rates as funding_rates_module
        
        # Set up expired cached data
        old_data = [{'market': 'OLD-USD', 'dexRates': []}]
        funding_rates_module._cache = {
            'data': old_data,
            'last_update': 1640995200.0  # Old timestamp
        }
        
        # Mock fresh data
        mock_fetch.return_value = {'dydx': {'BTC': 87.6}, 'hyperliquid': {'BTC': 70.08}}
        
        # Create handler instance
        handler_instance = handler()
        handler_instance.send_response = MagicMock()
        handler_instance.send_header = MagicMock()
        handler_instance.end_headers = MagicMock()
        handler_instance.wfile = MagicMock()
        
        # Call after cache expiration (600+ seconds later)
        with patch('time.time', return_value=1640996000.0), \
             patch('api.funding_rates.combine_funding_data') as mock_combine:
            
            mock_combine.return_value = [{'market': 'BTC-USD', 'dexRates': []}]
            
            handler_instance.do_GET()
        
        # Should fetch new data
        mock_fetch.assert_called_once()
        mock_combine.assert_called_once()

    @pytest.mark.integration
    @patch('api.funding_rates.fetch_all_funding_rates')
    def test_funding_rates_handler_error(self, mock_fetch):
        """Test funding rates handler with fetch error."""
        from api.funding_rates import handler
        
        # Mock fetch error
        mock_fetch.side_effect = Exception("API Error")
        
        # Create handler instance
        handler_instance = handler()
        handler_instance.send_response = MagicMock()
        handler_instance.send_header = MagicMock()
        handler_instance.end_headers = MagicMock()
        handler_instance.wfile = MagicMock()
        
        handler_instance.do_GET()
        
        # Should return error response
        written_calls = handler_instance.wfile.write.call_args_list
        response_data = json.loads(written_calls[0][0][0].decode())
        
        assert 'error' in response_data
        assert response_data['error'] == 'Unable to fetch funding rates'

    @pytest.mark.integration
    def test_funding_rates_handler_options(self):
        """Test funding rates handler OPTIONS method for CORS."""
        from api.funding_rates import handler
        
        # Create handler instance
        handler_instance = handler()
        handler_instance.send_response = MagicMock()
        handler_instance.send_header = MagicMock()
        handler_instance.end_headers = MagicMock()
        
        handler_instance.do_OPTIONS()
        
        # Verify CORS headers
        handler_instance.send_response.assert_called_with(200)
        
        expected_headers = [
            ('Access-Control-Allow-Origin', '*'),
            ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'),
            ('Access-Control-Allow-Headers', 'Content-Type')
        ]
        
        for header_name, header_value in expected_headers:
            handler_instance.send_header.assert_any_call(header_name, header_value)


class TestVercelHealthHandler:
    """Test Vercel health check serverless function."""

    @pytest.mark.integration
    def test_health_handler_success(self):
        """Test successful health check handler execution."""
        from api.health import handler
        
        # Create handler instance
        handler_instance = handler()
        handler_instance.send_response = MagicMock()
        handler_instance.send_header = MagicMock()
        handler_instance.end_headers = MagicMock()
        handler_instance.wfile = MagicMock()
        
        handler_instance.do_GET()
        
        # Verify response
        handler_instance.send_response.assert_called_with(200)
        handler_instance.send_header.assert_any_call('Content-type', 'application/json')
        handler_instance.send_header.assert_any_call('Access-Control-Allow-Origin', '*')
        
        # Verify response data
        written_calls = handler_instance.wfile.write.call_args_list
        assert len(written_calls) == 1
        
        response_data = json.loads(written_calls[0][0][0].decode())
        assert 'status' in response_data
        assert 'timestamp' in response_data
        assert 'message' in response_data
        assert response_data['status'] == 'healthy'
        assert 'Vercel' in response_data['message']

    @pytest.mark.integration
    def test_health_handler_options(self):
        """Test health handler OPTIONS method for CORS."""
        from api.health import handler
        
        # Create handler instance
        handler_instance = handler()
        handler_instance.send_response = MagicMock()
        handler_instance.send_header = MagicMock()
        handler_instance.end_headers = MagicMock()
        
        handler_instance.do_OPTIONS()
        
        # Verify CORS headers
        handler_instance.send_response.assert_called_with(200)
        
        expected_headers = [
            ('Access-Control-Allow-Origin', '*'),
            ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'),
            ('Access-Control-Allow-Headers', 'Content-Type')
        ]
        
        for header_name, header_value in expected_headers:
            handler_instance.send_header.assert_any_call(header_name, header_value)

    @pytest.mark.integration
    def test_health_response_structure(self):
        """Test health handler response structure."""
        from api.health import handler
        
        # Create handler instance
        handler_instance = handler()
        handler_instance.send_response = MagicMock()
        handler_instance.send_header = MagicMock()
        handler_instance.end_headers = MagicMock()
        handler_instance.wfile = MagicMock()
        
        with patch('api.health.datetime') as mock_datetime:
            mock_datetime.now.return_value.isoformat.return_value = '2022-01-01T12:00:00'
            
            handler_instance.do_GET()
        
        # Verify response structure
        written_calls = handler_instance.wfile.write.call_args_list
        response_data = json.loads(written_calls[0][0][0].decode())
        
        # Check required fields
        assert 'status' in response_data
        assert 'timestamp' in response_data
        assert 'message' in response_data
        
        # Check values
        assert response_data['status'] == 'healthy'
        assert response_data['timestamp'] == '2022-01-01T12:00:00'
        assert isinstance(response_data['message'], str)


class TestVercelIntegration:
    """Test integration aspects of Vercel functions."""

    @pytest.mark.integration
    @patch('api.funding_rates.get_dydx_funding_rates')
    @patch('api.funding_rates.get_hyperliquid_funding_rates')
    @patch('api.funding_rates.get_paradex_funding_rates')
    @patch('api.funding_rates.get_extended_funding_rates')
    def test_vercel_dex_integration(
        self, 
        mock_extended,
        mock_paradex,
        mock_hyperliquid,
        mock_dydx
    ):
        """Test Vercel function integration with all DEX fetchers."""
        from api.funding_rates import handler, fetch_all_funding_rates
        
        # Setup mock returns
        mock_dydx.return_value = {'BTC': 87.6, 'ETH': 43.8}
        mock_hyperliquid.return_value = {'BTC': 70.08, 'SOL': -8.76}
        mock_paradex.return_value = {'ETH': 32.85}
        mock_extended.return_value = {'BTC': 61.32, 'SOL': -7.008}
        
        # Test the fetch function used by the handler
        results = fetch_all_funding_rates()
        
        assert 'dydx' in results
        assert 'hyperliquid' in results
        assert 'paradex' in results
        assert 'extended' in results
        
        # Verify all DEX functions were called
        mock_dydx.assert_called_once()
        mock_hyperliquid.assert_called_once()
        mock_paradex.assert_called_once()
        mock_extended.assert_called_once()

    @pytest.mark.integration
    def test_vercel_cache_behavior(self):
        """Test Vercel function cache behavior over time."""
        from api.funding_rates import handler
        import api.funding_rates as funding_rates_module
        
        # Start with empty cache
        funding_rates_module._cache = {
            'data': [],
            'last_update': None
        }
        
        # Create handler instance
        handler_instance = handler()
        handler_instance.send_response = MagicMock()
        handler_instance.send_header = MagicMock()
        handler_instance.end_headers = MagicMock()
        handler_instance.wfile = MagicMock()
        
        with patch('api.funding_rates.fetch_all_funding_rates') as mock_fetch, \
             patch('api.funding_rates.combine_funding_data') as mock_combine:
            
            mock_fetch.return_value = {'dydx': {'BTC': 87.6}}
            mock_combine.return_value = [{'market': 'BTC-USD', 'dexRates': []}]
            
            # First call should fetch data
            with patch('time.time', return_value=1640995200.0):
                handler_instance.do_GET()
            
            assert mock_fetch.call_count == 1
            
            # Reset mocks
            mock_fetch.reset_mock()
            mock_combine.reset_mock()
            
            # Second call within cache period should not fetch
            with patch('time.time', return_value=1640995400.0):  # 200 seconds later
                handler_instance.do_GET()
            
            assert mock_fetch.call_count == 0  # Should use cache
            
            # Third call after cache expiry should fetch again
            with patch('time.time', return_value=1640996000.0):  # 800 seconds later
                handler_instance.do_GET()
            
            assert mock_fetch.call_count == 1  # Should fetch new data