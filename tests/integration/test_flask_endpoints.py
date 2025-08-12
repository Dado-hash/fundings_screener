"""Integration tests for Flask API endpoints."""

import json
import pytest
import time
from unittest.mock import patch, MagicMock

# Import Flask app for testing
from backend.app import app


class TestFlaskApp:
    """Test Flask application endpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client for the Flask app."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        
        with app.test_client() as client:
            yield client

    @pytest.fixture(autouse=True)
    def reset_app_state(self):
        """Reset Flask app global state before each test."""
        import backend.app as app_module
        app_module.funding_cache = {}
        app_module.last_update = None
        app_module.app_initialized = False
        app_module.background_thread = None

    @pytest.mark.integration
    def test_health_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get('/api/health')
        
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'application/json'
        
        data = json.loads(response.data)
        assert 'status' in data
        assert 'timestamp' in data
        assert 'cache_age' in data
        assert data['status'] == 'healthy'

    @pytest.mark.integration
    @patch('backend.app.fetch_all_funding_rates')
    @patch('backend.app.combine_funding_data')
    @patch('backend.app.start_background_updates')
    def test_funding_rates_first_startup(
        self, 
        mock_start_bg,
        mock_combine, 
        mock_fetch,
        client
    ):
        """Test funding rates endpoint on first startup."""
        # Mock the data fetching and combination
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
        
        with patch('time.time', return_value=1640995200.0):
            response = client.get('/api/funding-rates')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'data' in data
        assert 'lastUpdate' in data
        assert 'totalMarkets' in data
        
        assert len(data['data']) == 1
        assert data['data'][0]['market'] == 'BTC-USD'
        assert data['totalMarkets'] == 1
        
        # Should have called startup functions
        mock_fetch.assert_called_once()
        mock_combine.assert_called_once_with(mock_dex_data)
        mock_start_bg.assert_called_once()

    @pytest.mark.integration
    def test_funding_rates_cached_data(self, client):
        """Test funding rates endpoint with cached data."""
        import backend.app as app_module
        
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
        
        app_module.funding_cache = cached_data
        app_module.last_update = 1640995200.0
        app_module.app_initialized = True
        
        response = client.get('/api/funding-rates')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['data'] == cached_data
        assert data['totalMarkets'] == 1

    @pytest.mark.integration
    @patch('backend.app.fetch_all_funding_rates')
    def test_funding_rates_fetch_error(self, mock_fetch, client):
        """Test funding rates endpoint with fetch error on first startup."""
        mock_fetch.side_effect = Exception("API Error")
        
        response = client.get('/api/funding-rates')
        
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Unable to fetch funding rates'

    @pytest.mark.integration
    def test_funding_rates_no_data_available(self, client):
        """Test funding rates endpoint with no cached data."""
        import backend.app as app_module
        
        # Set initialized but empty cache
        app_module.funding_cache = []
        app_module.app_initialized = True
        
        response = client.get('/api/funding-rates')
        
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'No data available'

    @pytest.mark.integration
    def test_cors_headers(self, client):
        """Test that CORS headers are properly set."""
        response = client.get('/api/health')
        
        assert response.status_code == 200
        assert 'Access-Control-Allow-Origin' in response.headers
        assert response.headers['Access-Control-Allow-Origin'] == '*'

    @pytest.mark.integration
    def test_funding_rates_response_structure(self, client):
        """Test the structure of funding rates response."""
        import backend.app as app_module
        
        # Set up well-structured cached data
        cached_data = [
            {
                'market': 'BTC-USD',
                'dexRates': [
                    {'dex': 'dYdX', 'rate': 87.6},
                    {'dex': 'Hyperliquid', 'rate': 70.08},
                    {'dex': 'Paradex', 'rate': 65.7}
                ],
                'volume24h': 0,
                'openInterest': 0,
                'lastUpdate': '2022-01-01T12:00:00'
            },
            {
                'market': 'ETH-USD', 
                'dexRates': [
                    {'dex': 'dYdX', 'rate': 43.8},
                    {'dex': 'Extended', 'rate': 30.66}
                ],
                'volume24h': 0,
                'openInterest': 0,
                'lastUpdate': '2022-01-01T12:00:00'
            }
        ]
        
        app_module.funding_cache = cached_data
        app_module.last_update = 1640995200.0
        app_module.app_initialized = True
        
        response = client.get('/api/funding-rates')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        
        # Check top-level structure
        assert 'data' in data
        assert 'lastUpdate' in data
        assert 'totalMarkets' in data
        
        assert isinstance(data['data'], list)
        assert len(data['data']) == 2
        assert data['totalMarkets'] == 2
        assert data['lastUpdate'] is not None
        
        # Check individual market structure
        for market in data['data']:
            assert 'market' in market
            assert 'dexRates' in market
            assert 'volume24h' in market
            assert 'openInterest' in market
            assert 'lastUpdate' in market
            
            assert isinstance(market['dexRates'], list)
            assert len(market['dexRates']) >= 2
            
            for rate in market['dexRates']:
                assert 'dex' in rate
                assert 'rate' in rate
                assert isinstance(rate['dex'], str)
                assert isinstance(rate['rate'], (int, float))

    @pytest.mark.integration
    @patch('backend.app.fetch_all_funding_rates')
    @patch('backend.app.combine_funding_data')
    @patch('backend.app.start_background_updates') 
    def test_concurrent_requests_first_startup(
        self,
        mock_start_bg,
        mock_combine,
        mock_fetch,
        client
    ):
        """Test multiple concurrent requests during first startup."""
        import threading
        import time
        
        mock_dex_data = {
            'dydx': {'BTC': 87.6}
        }
        mock_combined_data = [
            {
                'market': 'BTC-USD',
                'dexRates': [{'dex': 'dYdX', 'rate': 87.6}],
                'volume24h': 0,
                'openInterest': 0,
                'lastUpdate': '2022-01-01T12:00:00'
            }
        ]
        
        # Add delay to simulate slow API calls
        def slow_fetch():
            time.sleep(0.1)
            return mock_dex_data
            
        mock_fetch.side_effect = slow_fetch
        mock_combine.return_value = mock_combined_data
        
        responses = []
        
        def make_request():
            with patch('time.time', return_value=1640995200.0):
                resp = client.get('/api/funding-rates')
                responses.append(resp)
        
        # Start multiple requests concurrently
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'data' in data


class TestFlaskErrorHandling:
    """Test error handling in Flask endpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client for the Flask app."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    @pytest.fixture(autouse=True) 
    def reset_app_state(self):
        """Reset Flask app global state before each test."""
        import backend.app as app_module
        app_module.funding_cache = {}
        app_module.last_update = None
        app_module.app_initialized = False
        app_module.background_thread = None

    @pytest.mark.integration
    def test_invalid_endpoint(self, client):
        """Test accessing invalid endpoint."""
        response = client.get('/api/invalid')
        
        assert response.status_code == 404

    @pytest.mark.integration
    def test_wrong_http_method(self, client):
        """Test using wrong HTTP method."""
        response = client.post('/api/health')
        
        assert response.status_code == 405

    @pytest.mark.integration
    @patch('backend.app.datetime')
    def test_health_with_cache_age(self, mock_datetime, client):
        """Test health endpoint with cache age calculation."""
        import backend.app as app_module
        
        # Set up cached data with known timestamp
        app_module.last_update = 1640995200.0
        mock_datetime.now.return_value.isoformat.return_value = '2022-01-01T12:00:00'
        
        with patch('time.time', return_value=1640995260.0):  # 60 seconds later
            response = client.get('/api/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['cache_age'] == 60.0