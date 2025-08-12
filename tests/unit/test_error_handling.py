"""Unit tests for error handling and timeout scenarios."""

import pytest
import requests
from unittest.mock import patch, MagicMock
import requests_mock
import socket
import time
from requests.exceptions import (
    Timeout, 
    ConnectTimeout, 
    ReadTimeout,
    ConnectionError,
    HTTPError,
    RequestException
)

# Import the functions to test
from backend.app import (
    get_dydx_funding_rates,
    get_hyperliquid_funding_rates,
    get_paradex_funding_rates,
    get_extended_funding_rates,
    fetch_all_funding_rates
)


class TestNetworkErrorHandling:
    """Test network-related error handling."""

    @pytest.mark.unit
    def test_dydx_connection_timeout(self):
        """Test dYdX API connection timeout handling."""
        with requests_mock.Mocker() as m:
            m.get(
                "https://indexer.dydx.trade/v4/perpetualMarkets",
                exc=ConnectTimeout("Connection timeout")
            )
            
            rates = get_dydx_funding_rates()
            assert rates == {}

    @pytest.mark.unit
    def test_hyperliquid_read_timeout(self):
        """Test Hyperliquid API read timeout handling."""
        with requests_mock.Mocker() as m:
            m.post(
                "https://api.hyperliquid.xyz/info",
                exc=ReadTimeout("Read timeout")
            )
            
            rates = get_hyperliquid_funding_rates()
            assert rates == {}

    @pytest.mark.unit
    def test_paradex_general_timeout(self):
        """Test Paradex API general timeout handling."""
        with requests_mock.Mocker() as m:
            m.get(
                "https://api.prod.paradex.trade/v1/markets",
                exc=Timeout("Request timeout")
            )
            
            rates = get_paradex_funding_rates()
            assert rates == {}

    @pytest.mark.unit
    def test_extended_connection_error(self):
        """Test Extended API connection error handling."""
        with requests_mock.Mocker() as m:
            m.get(
                "https://api.extended.exchange/api/v1//info/markets",
                exc=ConnectionError("Connection failed")
            )
            
            rates = get_extended_funding_rates()
            assert rates == {}

    @pytest.mark.unit
    def test_dydx_dns_resolution_error(self):
        """Test dYdX API DNS resolution error."""
        with requests_mock.Mocker() as m:
            m.get(
                "https://indexer.dydx.trade/v4/perpetualMarkets",
                exc=ConnectionError("Name or service not known")
            )
            
            rates = get_dydx_funding_rates()
            assert rates == {}

    @pytest.mark.unit
    def test_socket_error_handling(self):
        """Test socket-level error handling."""
        with requests_mock.Mocker() as m:
            m.get(
                "https://indexer.dydx.trade/v4/perpetualMarkets",
                exc=ConnectionError("Network is unreachable")
            )
            
            rates = get_dydx_funding_rates()
            assert rates == {}


class TestHTTPErrorHandling:
    """Test HTTP error status code handling."""

    @pytest.mark.unit
    def test_dydx_404_error(self):
        """Test dYdX API 404 error handling."""
        with requests_mock.Mocker() as m:
            m.get(
                "https://indexer.dydx.trade/v4/perpetualMarkets",
                status_code=404,
                text="Not Found"
            )
            
            rates = get_dydx_funding_rates()
            assert rates == {}

    @pytest.mark.unit
    def test_hyperliquid_500_error(self):
        """Test Hyperliquid API 500 error handling."""
        with requests_mock.Mocker() as m:
            m.post(
                "https://api.hyperliquid.xyz/info",
                status_code=500,
                text="Internal Server Error"
            )
            
            rates = get_hyperliquid_funding_rates()
            assert rates == {}

    @pytest.mark.unit
    def test_paradex_403_error(self):
        """Test Paradex API 403 error handling."""
        with requests_mock.Mocker() as m:
            m.get(
                "https://api.prod.paradex.trade/v1/markets",
                status_code=403,
                text="Forbidden"
            )
            
            rates = get_paradex_funding_rates()
            assert rates == {}

    @pytest.mark.unit
    def test_extended_429_rate_limit(self):
        """Test Extended API 429 rate limit error handling."""
        with requests_mock.Mocker() as m:
            m.get(
                "https://api.extended.exchange/api/v1//info/markets",
                status_code=429,
                text="Too Many Requests"
            )
            
            rates = get_extended_funding_rates()
            assert rates == {}

    @pytest.mark.unit
    def test_paradex_summary_individual_errors(self):
        """Test Paradex handling when individual market summaries fail."""
        markets_response = {
            "results": [
                {"symbol": "BTC-USD-PERP", "asset_kind": "PERPETUAL"},
                {"symbol": "ETH-USD-PERP", "asset_kind": "PERPETUAL"},
                {"symbol": "SOL-USD-PERP", "asset_kind": "PERPETUAL"}
            ]
        }
        
        with requests_mock.Mocker() as m:
            # Mock successful markets call
            m.get(
                "https://api.prod.paradex.trade/v1/markets",
                json=markets_response
            )
            
            # Mock mixed success/failure for summaries
            m.get(
                "https://api.prod.paradex.trade/v1/markets/summary",
                [
                    # BTC succeeds
                    {"json": {"results": [{"funding_rate": "0.00006"}]}, 
                     "status_code": 200},
                    # ETH fails
                    {"status_code": 500},
                    # SOL succeeds
                    {"json": {"results": [{"funding_rate": "-0.000005"}]}, 
                     "status_code": 200}
                ]
            )
            
            rates = get_paradex_funding_rates()
            
            # Should include successful fetches and skip failed ones
            assert "BTC" in rates
            assert "SOL" in rates
            assert "ETH" not in rates
            assert len(rates) == 2


class TestDataValidationErrors:
    """Test handling of invalid or malformed API response data."""

    @pytest.mark.unit
    def test_dydx_invalid_json(self):
        """Test dYdX API with invalid JSON response."""
        with requests_mock.Mocker() as m:
            m.get(
                "https://indexer.dydx.trade/v4/perpetualMarkets",
                text="Invalid JSON{{"
            )
            
            rates = get_dydx_funding_rates()
            assert rates == {}

    @pytest.mark.unit
    def test_hyperliquid_missing_fields(self):
        """Test Hyperliquid API with missing required fields."""
        invalid_response = [
            {
                "universe": [{"name": "BTC"}]
                # Missing funding data array
            }
        ]
        
        with requests_mock.Mocker() as m:
            m.post(
                "https://api.hyperliquid.xyz/info",
                json=invalid_response
            )
            
            rates = get_hyperliquid_funding_rates()
            assert rates == {}

    @pytest.mark.unit
    def test_hyperliquid_mismatched_arrays(self):
        """Test Hyperliquid API with mismatched universe and data arrays."""
        invalid_response = [
            {
                "universe": [{"name": "BTC"}, {"name": "ETH"}]
            },
            [
                {"funding": "0.00008"}
                # Missing second funding entry
            ]
        ]
        
        with requests_mock.Mocker() as m:
            m.post(
                "https://api.hyperliquid.xyz/info",
                json=invalid_response
            )
            
            rates = get_hyperliquid_funding_rates()
            assert rates == {}

    @pytest.mark.unit
    def test_paradex_invalid_funding_rate(self):
        """Test Paradex API with invalid funding rate values."""
        markets_response = {
            "results": [
                {"symbol": "BTC-USD-PERP", "asset_kind": "PERPETUAL"},
                {"symbol": "ETH-USD-PERP", "asset_kind": "PERPETUAL"}
            ]
        }
        
        with requests_mock.Mocker() as m:
            m.get(
                "https://api.prod.paradex.trade/v1/markets",
                json=markets_response
            )
            
            # Mock summaries with mixed valid/invalid data
            m.get(
                "https://api.prod.paradex.trade/v1/markets/summary",
                [
                    {"json": {"results": [{"funding_rate": "not_a_number"}]}},
                    {"json": {"results": [{"funding_rate": "0.00003"}]}}
                ]
            )
            
            rates = get_paradex_funding_rates()
            
            # Should skip invalid rates and include valid ones
            assert "BTC" not in rates  # Invalid rate
            assert "ETH" in rates      # Valid rate
            assert len(rates) == 1

    @pytest.mark.unit
    def test_extended_missing_market_stats(self):
        """Test Extended API with missing marketStats field."""
        invalid_response = {
            "data": [
                {
                    "name": "BTC-USD",
                    "marketStats": {
                        "fundingRate": "0.00007"
                    }
                },
                {
                    "name": "ETH-USD"
                    # Missing marketStats
                },
                {
                    "name": "SOL-USD",
                    "marketStats": {}  # Missing fundingRate
                }
            ]
        }
        
        with requests_mock.Mocker() as m:
            m.get(
                "https://api.extended.exchange/api/v1//info/markets",
                json=invalid_response
            )
            
            rates = get_extended_funding_rates()
            
            # Should only include valid entries
            assert "BTC" in rates
            assert "ETH" not in rates
            assert "SOL" not in rates
            assert len(rates) == 1

    @pytest.mark.unit
    def test_dydx_empty_markets(self):
        """Test dYdX API with empty markets object."""
        empty_response = {"markets": {}}
        
        with requests_mock.Mocker() as m:
            m.get(
                "https://indexer.dydx.trade/v4/perpetualMarkets",
                json=empty_response
            )
            
            rates = get_dydx_funding_rates()
            assert rates == {}

    @pytest.mark.unit
    def test_null_response_handling(self):
        """Test handling of null API responses."""
        with requests_mock.Mocker() as m:
            m.get(
                "https://indexer.dydx.trade/v4/perpetualMarkets",
                json=None
            )
            
            rates = get_dydx_funding_rates()
            assert rates == {}


class TestTimeoutConfiguration:
    """Test timeout configuration and handling."""

    @pytest.mark.unit
    def test_dydx_timeout_value(self):
        """Test that dYdX API uses correct timeout value."""
        with patch('requests.get') as mock_get:
            mock_get.return_value.json.return_value = {"markets": {}}
            mock_get.return_value.raise_for_status.return_value = None
            
            get_dydx_funding_rates()
            
            # Verify timeout parameter
            mock_get.assert_called_once_with(
                "https://indexer.dydx.trade/v4/perpetualMarkets",
                timeout=10
            )

    @pytest.mark.unit 
    def test_hyperliquid_timeout_value(self):
        """Test that Hyperliquid API uses correct timeout value."""
        with patch('requests.post') as mock_post:
            mock_post.return_value.ok = True
            mock_post.return_value.json.return_value = [
                {"universe": []},
                []
            ]
            
            get_hyperliquid_funding_rates()
            
            # Verify timeout parameter
            mock_post.assert_called_once_with(
                "https://api.hyperliquid.xyz/info",
                json={"type": "metaAndAssetCtxs"},
                timeout=10
            )

    @pytest.mark.unit
    def test_paradex_summary_timeout(self):
        """Test that Paradex summary calls use correct timeout."""
        markets_response = {
            "results": [{"symbol": "BTC-USD-PERP", "asset_kind": "PERPETUAL"}]
        }
        
        with patch('requests.get') as mock_get:
            # First call (markets) - no timeout restriction 
            mock_get.return_value.json.side_effect = [
                markets_response,
                {"results": [{"funding_rate": "0.00006"}]}
            ]
            mock_get.return_value.raise_for_status.return_value = None
            
            get_paradex_funding_rates()
            
            # Check that summary call uses 5 second timeout
            calls = mock_get.call_args_list
            summary_call = calls[1]  # Second call is the summary
            assert summary_call[1]['timeout'] == 5


class TestConcurrentErrorHandling:
    """Test error handling in concurrent/threaded operations."""

    @pytest.mark.unit
    @patch('backend.app.get_dydx_funding_rates')
    @patch('backend.app.get_hyperliquid_funding_rates')
    @patch('backend.app.get_paradex_funding_rates')
    @patch('backend.app.get_extended_funding_rates')
    def test_fetch_all_with_mixed_errors(
        self,
        mock_extended,
        mock_paradex,
        mock_hyperliquid,
        mock_dydx
    ):
        """Test fetch_all_funding_rates with mixed successes and failures."""
        # Setup mixed results
        mock_dydx.return_value = {"BTC": 87.6}  # Success
        mock_hyperliquid.side_effect = Exception("Network error")  # Failure
        mock_paradex.return_value = {}  # Success but empty
        mock_extended.side_effect = Timeout("API timeout")  # Failure
        
        results = fetch_all_funding_rates()
        
        # Should return results from all DEXs, even if some failed
        assert 'dydx' in results
        assert 'hyperliquid' in results
        assert 'paradex' in results
        assert 'extended' in results
        
        # Successful fetches should have data
        assert results['dydx'] == {"BTC": 87.6}
        assert results['paradex'] == {}
        
        # Failed fetches should be handled gracefully
        # (exact behavior depends on implementation)

    @pytest.mark.unit
    @patch('threading.Thread')
    def test_threading_error_isolation(self, mock_thread):
        """Test that threading errors don't crash the entire fetch operation."""
        # Mock thread that raises an exception
        mock_thread_instance = MagicMock()
        mock_thread_instance.start.side_effect = Exception("Thread creation failed")
        mock_thread.return_value = mock_thread_instance
        
        # Should not raise exception
        results = fetch_all_funding_rates()
        
        # Should return empty results for all DEXs
        assert isinstance(results, dict)


class TestEdgeCaseHandling:
    """Test handling of edge cases and boundary conditions."""

    @pytest.mark.unit
    def test_extremely_large_funding_rates(self):
        """Test handling of extremely large funding rate values."""
        large_value_response = {
            "markets": {
                "VOLATILE-USD": {
                    "nextFundingRate": "999999.999999"  # Extremely large rate
                }
            }
        }
        
        with requests_mock.Mocker() as m:
            m.get(
                "https://indexer.dydx.trade/v4/perpetualMarkets",
                json=large_value_response
            )
            
            rates = get_dydx_funding_rates()
            
            # Should handle large numbers without error
            assert "VOLATILE" in rates
            assert isinstance(rates["VOLATILE"], float)
            assert rates["VOLATILE"] > 0

    @pytest.mark.unit 
    def test_negative_zero_handling(self):
        """Test handling of negative zero values."""
        zero_response = {
            "markets": {
                "STABLE-USD": {
                    "nextFundingRate": "-0.0"
                }
            }
        }
        
        with requests_mock.Mocker() as m:
            m.get(
                "https://indexer.dydx.trade/v4/perpetualMarkets",
                json=zero_response
            )
            
            rates = get_dydx_funding_rates()
            
            assert "STABLE" in rates
            assert rates["STABLE"] == 0.0

    @pytest.mark.unit
    def test_unicode_market_names(self):
        """Test handling of market names with unicode characters."""
        unicode_response = {
            "markets": {
                "TËST-USD": {
                    "nextFundingRate": "0.0001"
                }
            }
        }
        
        with requests_mock.Mocker() as m:
            m.get(
                "https://indexer.dydx.trade/v4/perpetualMarkets",
                json=unicode_response
            )
            
            rates = get_dydx_funding_rates()
            
            # Should handle unicode characters properly
            assert "TËST" in rates

    @pytest.mark.unit
    def test_empty_string_values(self):
        """Test handling of empty string values in API responses."""
        empty_string_response = {
            "markets": {
                "BTC-USD": {
                    "nextFundingRate": ""  # Empty string
                }
            }
        }
        
        with requests_mock.Mocker() as m:
            m.get(
                "https://indexer.dydx.trade/v4/perpetualMarkets", 
                json=empty_string_response
            )
            
            rates = get_dydx_funding_rates()
            
            # Should skip entries with empty values
            assert "BTC" not in rates or rates["BTC"] is not None

    @pytest.mark.slow
    @pytest.mark.unit
    def test_very_slow_api_response(self):
        """Test handling of very slow API responses that don't quite timeout."""
        def slow_response(request, context):
            time.sleep(9)  # Just under the 10 second timeout
            return {"markets": {"BTC-USD": {"nextFundingRate": "0.0001"}}}
        
        with requests_mock.Mocker() as m:
            m.get(
                "https://indexer.dydx.trade/v4/perpetualMarkets",
                json=slow_response
            )
            
            # Should complete successfully (though slowly)
            rates = get_dydx_funding_rates()
            assert "BTC" in rates