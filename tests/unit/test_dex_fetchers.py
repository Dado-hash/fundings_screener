"""Unit tests for individual DEX API fetcher functions."""

import pytest
import requests
from unittest.mock import patch, MagicMock
import requests_mock

# Import the functions to test
from backend.app import (
    get_dydx_funding_rates,
    get_hyperliquid_funding_rates,
    get_paradex_funding_rates,
    get_extended_funding_rates,
    fetch_all_funding_rates
)


class TestDydxFetcher:
    """Test dYdX funding rates fetcher."""

    @pytest.mark.unit
    def test_get_dydx_funding_rates_success(self, mock_dydx_response, expected_dydx_rates):
        """Test successful dYdX API call."""
        with requests_mock.Mocker() as m:
            m.get(
                "https://indexer.dydx.trade/v4/perpetualMarkets",
                json=mock_dydx_response
            )
            
            rates = get_dydx_funding_rates()
            
            assert rates == expected_dydx_rates
            assert "BTC" in rates
            assert "ETH" in rates
            assert "SOL" in rates

    @pytest.mark.unit
    def test_get_dydx_funding_rates_network_error(self):
        """Test dYdX API call with network error."""
        with requests_mock.Mocker() as m:
            m.get(
                "https://indexer.dydx.trade/v4/perpetualMarkets",
                exc=requests.exceptions.ConnectTimeout
            )
            
            rates = get_dydx_funding_rates()
            
            assert rates == {}

    @pytest.mark.unit  
    def test_get_dydx_funding_rates_http_error(self):
        """Test dYdX API call with HTTP error."""
        with requests_mock.Mocker() as m:
            m.get(
                "https://indexer.dydx.trade/v4/perpetualMarkets",
                status_code=500
            )
            
            rates = get_dydx_funding_rates()
            
            assert rates == {}

    @pytest.mark.unit
    def test_get_dydx_funding_rates_malformed_data(self):
        """Test dYdX API with malformed response data."""
        malformed_response = {
            "markets": {
                "BTC-USD": {
                    "nextFundingRate": "invalid_number"
                },
                "ETH-USD": {
                    "nextFundingRate": "0.00005"
                }
            }
        }
        
        with requests_mock.Mocker() as m:
            m.get(
                "https://indexer.dydx.trade/v4/perpetualMarkets",
                json=malformed_response
            )
            
            rates = get_dydx_funding_rates()
            
            # Should skip invalid entries and only return valid ones
            assert "BTC" not in rates
            assert "ETH" in rates
            assert len(rates) == 1

    @pytest.mark.unit
    def test_get_dydx_funding_rates_timeout(self):
        """Test dYdX API call timeout handling."""
        with requests_mock.Mocker() as m:
            m.get(
                "https://indexer.dydx.trade/v4/perpetualMarkets",
                exc=requests.exceptions.Timeout
            )
            
            rates = get_dydx_funding_rates()
            
            assert rates == {}


class TestHyperliquidFetcher:
    """Test Hyperliquid funding rates fetcher."""

    @pytest.mark.unit
    def test_get_hyperliquid_funding_rates_success(self, mock_hyperliquid_response, expected_hyperliquid_rates):
        """Test successful Hyperliquid API call."""
        with requests_mock.Mocker() as m:
            m.post(
                "https://api.hyperliquid.xyz/info",
                json=mock_hyperliquid_response
            )
            
            rates = get_hyperliquid_funding_rates()
            
            assert rates == expected_hyperliquid_rates
            assert "BTC" in rates
            assert "ETH" in rates
            assert "SOL" in rates

    @pytest.mark.unit
    def test_get_hyperliquid_funding_rates_network_error(self):
        """Test Hyperliquid API call with network error."""
        with requests_mock.Mocker() as m:
            m.post(
                "https://api.hyperliquid.xyz/info",
                exc=requests.exceptions.ConnectTimeout
            )
            
            rates = get_hyperliquid_funding_rates()
            
            assert rates == {}

    @pytest.mark.unit
    def test_get_hyperliquid_funding_rates_http_error(self):
        """Test Hyperliquid API call with HTTP error."""
        with requests_mock.Mocker() as m:
            m.post(
                "https://api.hyperliquid.xyz/info",
                status_code=404
            )
            
            rates = get_hyperliquid_funding_rates()
            
            assert rates == {}

    @pytest.mark.unit
    def test_get_hyperliquid_funding_rates_malformed_data(self):
        """Test Hyperliquid API with malformed response data."""
        malformed_response = [
            {
                "universe": [
                    {"name": "BTC"},
                    {"name": "ETH"}
                ]
            },
            [
                {"funding": "invalid"},  # Invalid funding rate
                {"funding": "0.00004"}
            ]
        ]
        
        with requests_mock.Mocker() as m:
            m.post(
                "https://api.hyperliquid.xyz/info", 
                json=malformed_response
            )
            
            rates = get_hyperliquid_funding_rates()
            
            # Should handle the error gracefully
            assert rates == {}


class TestParadexFetcher:
    """Test Paradex funding rates fetcher."""

    @pytest.mark.unit
    def test_get_paradex_funding_rates_success(
        self, 
        mock_paradex_markets_response,
        mock_paradex_summary_response,
        expected_paradex_rates
    ):
        """Test successful Paradex API calls."""
        with requests_mock.Mocker() as m:
            # Mock markets endpoint
            m.get(
                "https://api.prod.paradex.trade/v1/markets",
                json=mock_paradex_markets_response
            )
            
            # Mock summary endpoints
            for market in ["BTC-USD-PERP", "ETH-USD-PERP", "SOL-USD-PERP"]:
                m.get(
                    "https://api.prod.paradex.trade/v1/markets/summary",
                    json=mock_paradex_summary_response(market),
                    additional_matcher=lambda req, market=market: req.qs.get("market") == [market]
                )
            
            rates = get_paradex_funding_rates()
            
            assert rates == expected_paradex_rates
            assert "BTC" in rates
            assert "ETH" in rates
            assert "SOL" in rates

    @pytest.mark.unit
    def test_get_paradex_funding_rates_markets_error(self):
        """Test Paradex markets endpoint error."""
        with requests_mock.Mocker() as m:
            m.get(
                "https://api.prod.paradex.trade/v1/markets",
                status_code=500
            )
            
            rates = get_paradex_funding_rates()
            
            assert rates == {}

    @pytest.mark.unit
    def test_get_paradex_funding_rates_summary_error(self, mock_paradex_markets_response):
        """Test Paradex summary endpoint error."""
        with requests_mock.Mocker() as m:
            # Mock successful markets call
            m.get(
                "https://api.prod.paradex.trade/v1/markets",
                json=mock_paradex_markets_response
            )
            
            # Mock failed summary calls
            m.get(
                "https://api.prod.paradex.trade/v1/markets/summary",
                status_code=500
            )
            
            rates = get_paradex_funding_rates()
            
            # Should return empty dict when all summary calls fail
            assert rates == {}


class TestExtendedFetcher:
    """Test Extended Exchange funding rates fetcher."""

    @pytest.mark.unit
    def test_get_extended_funding_rates_success(self, mock_extended_response, expected_extended_rates):
        """Test successful Extended API call."""
        with requests_mock.Mocker() as m:
            m.get(
                "https://api.extended.exchange/api/v1//info/markets",
                json=mock_extended_response
            )
            
            rates = get_extended_funding_rates()
            
            assert rates == expected_extended_rates
            assert "BTC" in rates
            assert "ETH" in rates
            assert "SOL" in rates

    @pytest.mark.unit
    def test_get_extended_funding_rates_network_error(self):
        """Test Extended API call with network error."""
        with requests_mock.Mocker() as m:
            m.get(
                "https://api.extended.exchange/api/v1//info/markets",
                exc=requests.exceptions.ConnectTimeout
            )
            
            rates = get_extended_funding_rates()
            
            assert rates == {}

    @pytest.mark.unit 
    def test_get_extended_funding_rates_malformed_data(self):
        """Test Extended API with malformed response data."""
        malformed_response = {
            "data": [
                {
                    "name": "BTC-USD",
                    "marketStats": {
                        "fundingRate": "invalid_rate"
                    }
                },
                {
                    "name": "ETH-USD",
                    "marketStats": {
                        "fundingRate": "0.000035"
                    }
                }
            ]
        }
        
        with requests_mock.Mocker() as m:
            m.get(
                "https://api.extended.exchange/api/v1//info/markets",
                json=malformed_response
            )
            
            rates = get_extended_funding_rates()
            
            # Should skip invalid entries and only return valid ones
            assert "BTC" not in rates
            assert "ETH" in rates
            assert len(rates) == 1


class TestFetchAllFundingRates:
    """Test the combined fetch function."""

    @pytest.mark.unit
    @patch('backend.app.get_dydx_funding_rates')
    @patch('backend.app.get_hyperliquid_funding_rates')
    @patch('backend.app.get_paradex_funding_rates')
    @patch('backend.app.get_extended_funding_rates')
    def test_fetch_all_funding_rates_success(
        self, 
        mock_extended,
        mock_paradex, 
        mock_hyperliquid,
        mock_dydx
    ):
        """Test fetching all funding rates successfully."""
        # Setup mock returns
        mock_dydx.return_value = {"BTC": 87.6, "ETH": 43.8}
        mock_hyperliquid.return_value = {"BTC": 70.08, "SOL": -8.76}
        mock_paradex.return_value = {"ETH": 32.85}
        mock_extended.return_value = {"BTC": 61.32, "SOL": -7.008}
        
        results = fetch_all_funding_rates()
        
        assert 'dydx' in results
        assert 'hyperliquid' in results
        assert 'paradex' in results
        assert 'extended' in results
        
        assert results['dydx'] == {"BTC": 87.6, "ETH": 43.8}
        assert results['hyperliquid'] == {"BTC": 70.08, "SOL": -8.76}
        assert results['paradex'] == {"ETH": 32.85}
        assert results['extended'] == {"BTC": 61.32, "SOL": -7.008}

    @pytest.mark.unit
    @patch('backend.app.get_dydx_funding_rates')
    @patch('backend.app.get_hyperliquid_funding_rates') 
    @patch('backend.app.get_paradex_funding_rates')
    @patch('backend.app.get_extended_funding_rates')
    def test_fetch_all_funding_rates_partial_failure(
        self,
        mock_extended,
        mock_paradex,
        mock_hyperliquid, 
        mock_dydx
    ):
        """Test fetching with some DEX failures."""
        # Setup mixed success/failure
        mock_dydx.return_value = {"BTC": 87.6}
        mock_hyperliquid.return_value = {}  # Failed
        mock_paradex.return_value = {"ETH": 32.85}
        mock_extended.return_value = {}  # Failed
        
        results = fetch_all_funding_rates()
        
        assert results['dydx'] == {"BTC": 87.6}
        assert results['hyperliquid'] == {}
        assert results['paradex'] == {"ETH": 32.85}
        assert results['extended'] == {}

    @pytest.mark.slow
    @pytest.mark.unit
    @patch('threading.Thread')
    def test_fetch_all_funding_rates_uses_threading(self, mock_thread):
        """Test that fetch_all_funding_rates uses threading."""
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance
        
        fetch_all_funding_rates()
        
        # Should create 4 threads (one for each DEX)
        assert mock_thread.call_count == 4
        
        # Should start and join all threads
        assert mock_thread_instance.start.call_count == 4
        assert mock_thread_instance.join.call_count == 4