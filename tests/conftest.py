"""Shared test fixtures and configuration."""

import json
import sys
import os
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
import requests_mock


# Add project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))
sys.path.insert(0, str(project_root / "api"))


@pytest.fixture
def mock_dydx_response():
    """Mock response for dYdX API."""
    return {
        "markets": {
            "BTC-USD": {
                "nextFundingRate": "0.0001",
                "status": "ONLINE"
            },
            "ETH-USD": {
                "nextFundingRate": "0.00005",
                "status": "ONLINE"
            },
            "SOL-USD": {
                "nextFundingRate": "-0.00002",
                "status": "ONLINE"
            }
        }
    }


@pytest.fixture
def mock_hyperliquid_response():
    """Mock response for Hyperliquid API."""
    return [
        {
            "universe": [
                {"name": "BTC"},
                {"name": "ETH"},
                {"name": "SOL"}
            ]
        },
        [
            {"funding": "0.00008"},
            {"funding": "0.00004"},
            {"funding": "-0.00001"}
        ]
    ]


@pytest.fixture
def mock_paradex_markets_response():
    """Mock response for Paradex markets API."""
    return {
        "results": [
            {
                "symbol": "BTC-USD-PERP",
                "asset_kind": "PERPETUAL"
            },
            {
                "symbol": "ETH-USD-PERP", 
                "asset_kind": "PERPETUAL"
            },
            {
                "symbol": "SOL-USD-PERP",
                "asset_kind": "PERPETUAL"
            }
        ]
    }


@pytest.fixture
def mock_paradex_summary_response():
    """Mock response for Paradex market summary API."""
    def _get_response(market):
        rates = {
            "BTC-USD-PERP": "0.00006",
            "ETH-USD-PERP": "0.00003", 
            "SOL-USD-PERP": "-0.000005"
        }
        return {
            "results": [{
                "funding_rate": rates.get(market, "0.0")
            }]
        }
    return _get_response


@pytest.fixture
def mock_extended_response():
    """Mock response for Extended Exchange API."""
    return {
        "data": [
            {
                "name": "BTC-USD",
                "marketStats": {
                    "fundingRate": "0.00007"
                }
            },
            {
                "name": "ETH-USD", 
                "marketStats": {
                    "fundingRate": "0.000035"
                }
            },
            {
                "name": "SOL-USD",
                "marketStats": {
                    "fundingRate": "-0.000008"
                }
            }
        ]
    }


@pytest.fixture
def expected_dydx_rates():
    """Expected parsed rates from dYdX."""
    return {
        "BTC": 0.0001 * 24 * 365 * 100,  # 87.6
        "ETH": 0.00005 * 24 * 365 * 100,  # 43.8
        "SOL": -0.00002 * 24 * 365 * 100  # -17.52
    }


@pytest.fixture
def expected_hyperliquid_rates():
    """Expected parsed rates from Hyperliquid."""
    return {
        "BTC": 0.00008 * 24 * 365 * 100,  # 70.08
        "ETH": 0.00004 * 24 * 365 * 100,  # 35.04
        "SOL": -0.00001 * 24 * 365 * 100  # -8.76
    }


@pytest.fixture
def expected_paradex_rates():
    """Expected parsed rates from Paradex."""
    return {
        "BTC": 0.00006 * 3 * 365 * 100,  # 65.7
        "ETH": 0.00003 * 3 * 365 * 100,  # 32.85
        "SOL": -0.000005 * 3 * 365 * 100  # -5.475
    }


@pytest.fixture
def expected_extended_rates():
    """Expected parsed rates from Extended."""
    return {
        "BTC": 0.00007 * 24 * 365 * 100,  # 61.32
        "ETH": 0.000035 * 24 * 365 * 100,  # 30.66
        "SOL": -0.000008 * 24 * 365 * 100  # -7.008
    }


@pytest.fixture
def mock_all_dex_responses(
    mock_dydx_response,
    mock_hyperliquid_response, 
    mock_paradex_markets_response,
    mock_paradex_summary_response,
    mock_extended_response
):
    """Mock all DEX API responses."""
    with requests_mock.Mocker() as m:
        # Mock dYdX
        m.get(
            "https://indexer.dydx.trade/v4/perpetualMarkets",
            json=mock_dydx_response
        )
        
        # Mock Hyperliquid
        m.post(
            "https://api.hyperliquid.xyz/info",
            json=mock_hyperliquid_response
        )
        
        # Mock Paradex markets
        m.get(
            "https://api.prod.paradex.trade/v1/markets",
            json=mock_paradex_markets_response
        )
        
        # Mock Paradex summaries
        for market in ["BTC-USD-PERP", "ETH-USD-PERP", "SOL-USD-PERP"]:
            m.get(
                "https://api.prod.paradex.trade/v1/markets/summary",
                json=mock_paradex_summary_response(market),
                additional_matcher=lambda req: req.qs.get("market") == [market]
            )
        
        # Mock Extended
        m.get(
            "https://api.extended.exchange/api/v1//info/markets",
            json=mock_extended_response
        )
        
        yield m


@pytest.fixture
def flask_app():
    """Create a Flask app instance for testing."""
    # Import here to avoid circular imports
    from backend.app import app
    
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def mock_threading():
    """Mock threading to avoid actual background threads in tests."""
    with patch('threading.Thread') as mock_thread:
        mock_instance = MagicMock()
        mock_thread.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_time():
    """Mock time functions for consistent testing."""
    with patch('time.time') as mock_time_func:
        mock_time_func.return_value = 1640995200.0  # Fixed timestamp
        yield mock_time_func


@pytest.fixture
def sample_combined_data():
    """Sample combined funding data for testing."""
    return [
        {
            'market': 'BTC-USD',
            'dexRates': [
                {'dex': 'dYdX', 'rate': 87.6},
                {'dex': 'Hyperliquid', 'rate': 70.08}
            ],
            'volume24h': 0,
            'openInterest': 0,
            'lastUpdate': '2022-01-01T00:00:00'
        },
        {
            'market': 'ETH-USD',
            'dexRates': [
                {'dex': 'dYdX', 'rate': 43.8},
                {'dex': 'Hyperliquid', 'rate': 35.04},
                {'dex': 'Paradex', 'rate': 32.85}
            ],
            'volume24h': 0,
            'openInterest': 0,
            'lastUpdate': '2022-01-01T00:00:00'
        }
    ]


@pytest.fixture(autouse=True)
def reset_flask_cache():
    """Reset Flask app cache before each test."""
    try:
        from backend.app import funding_cache, last_update, app_initialized
        funding_cache.clear()
        globals()['last_update'] = None
        globals()['app_initialized'] = False
    except ImportError:
        pass  # Module not imported yet


@pytest.fixture(autouse=True) 
def reset_vercel_cache():
    """Reset Vercel function cache before each test."""
    try:
        import api.funding_rates as funding_rates_module
        funding_rates_module._cache = {
            'data': [],
            'last_update': None
        }
    except ImportError:
        pass  # Module not imported yet