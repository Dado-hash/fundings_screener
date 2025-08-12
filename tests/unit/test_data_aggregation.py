"""Unit tests for data aggregation and combination logic."""

import pytest
from datetime import datetime
from unittest.mock import patch

# Import the function to test
from backend.app import combine_funding_data


class TestCombineFundingData:
    """Test the combine_funding_data function."""

    @pytest.mark.unit
    def test_combine_funding_data_success(self):
        """Test successful data combination from all DEXs."""
        dex_data = {
            'dydx': {
                'BTC': 87.6,
                'ETH': 43.8,
                'SOL': -17.52
            },
            'hyperliquid': {
                'BTC': 70.08,
                'ETH': 35.04,
                'AVAX': 25.0
            },
            'paradex': {
                'BTC': 65.7,
                'ETH': 32.85
            },
            'extended': {
                'BTC': 61.32,
                'SOL': -7.008,
                'DOT': 15.5
            }
        }
        
        result = combine_funding_data(dex_data)
        
        # Should have markets with at least 2 DEXs
        market_names = [item['market'] for item in result]
        assert 'BTC-USD' in market_names
        assert 'ETH-USD' in market_names
        # SOL only has dYdX and Extended (2 DEXs), should be included
        assert 'SOL-USD' in market_names
        # AVAX and DOT only have 1 DEX each, should be excluded
        assert 'AVAX-USD' not in market_names
        assert 'DOT-USD' not in market_names

    @pytest.mark.unit
    def test_combine_funding_data_btc_rates(self):
        """Test BTC rates combination from all DEXs."""
        dex_data = {
            'dydx': {'BTC': 87.6},
            'hyperliquid': {'BTC': 70.08},
            'paradex': {'BTC': 65.7},
            'extended': {'BTC': 61.32}
        }
        
        result = combine_funding_data(dex_data)
        
        btc_market = next(item for item in result if item['market'] == 'BTC-USD')
        
        # Should have all 4 DEX rates
        assert len(btc_market['dexRates']) == 4
        
        # Check individual rates
        dex_rates = {rate['dex']: rate['rate'] for rate in btc_market['dexRates']}
        assert dex_rates['dYdX'] == 87.6
        assert dex_rates['Hyperliquid'] == 70.08
        assert dex_rates['Paradex'] == 65.7
        assert dex_rates['Extended'] == 61.32

    @pytest.mark.unit
    def test_combine_funding_data_two_dex_minimum(self):
        """Test that markets need at least 2 DEXs to be included."""
        dex_data = {
            'dydx': {
                'BTC': 87.6,
                'RARE_COIN': 100.0  # Only on dYdX
            },
            'hyperliquid': {
                'BTC': 70.08,
                'ANOTHER_RARE': 50.0  # Only on Hyperliquid
            },
            'paradex': {},
            'extended': {}
        }
        
        result = combine_funding_data(dex_data)
        
        # Should only include BTC (appears on 2 DEXs)
        assert len(result) == 1
        assert result[0]['market'] == 'BTC-USD'
        
        # Rare coins with only 1 DEX should be excluded
        market_names = [item['market'] for item in result]
        assert 'RARE_COIN-USD' not in market_names
        assert 'ANOTHER_RARE-USD' not in market_names

    @pytest.mark.unit
    def test_combine_funding_data_empty_input(self):
        """Test combining with empty DEX data."""
        dex_data = {
            'dydx': {},
            'hyperliquid': {},
            'paradex': {},
            'extended': {}
        }
        
        result = combine_funding_data(dex_data)
        
        assert result == []

    @pytest.mark.unit
    def test_combine_funding_data_missing_dex(self):
        """Test combining with missing DEX data."""
        dex_data = {
            'dydx': {'BTC': 87.6, 'ETH': 43.8},
            'hyperliquid': {'BTC': 70.08}
            # paradex and extended missing
        }
        
        result = combine_funding_data(dex_data)
        
        # Should only include BTC (appears on 2 DEXs)
        assert len(result) == 1
        assert result[0]['market'] == 'BTC-USD'
        
        # ETH only on 1 DEX, should be excluded
        market_names = [item['market'] for item in result]
        assert 'ETH-USD' not in market_names

    @pytest.mark.unit
    def test_combine_funding_data_rate_rounding(self):
        """Test that rates are properly rounded to 2 decimal places."""
        dex_data = {
            'dydx': {'BTC': 87.123456789},
            'hyperliquid': {'BTC': 70.987654321}
        }
        
        result = combine_funding_data(dex_data)
        
        btc_market = result[0]
        dex_rates = {rate['dex']: rate['rate'] for rate in btc_market['dexRates']}
        
        assert dex_rates['dYdX'] == 87.12
        assert dex_rates['Hyperliquid'] == 70.99

    @pytest.mark.unit
    def test_combine_funding_data_structure(self):
        """Test the structure of combined data output."""
        dex_data = {
            'dydx': {'BTC': 87.6},
            'hyperliquid': {'BTC': 70.08}
        }
        
        with patch('backend.app.datetime') as mock_datetime:
            mock_datetime.now.return_value.isoformat.return_value = '2022-01-01T12:00:00'
            
            result = combine_funding_data(dex_data)
            
            market = result[0]
            
            # Check required fields
            assert 'market' in market
            assert 'dexRates' in market
            assert 'volume24h' in market
            assert 'openInterest' in market
            assert 'lastUpdate' in market
            
            # Check market format
            assert market['market'] == 'BTC-USD'
            
            # Check dexRates structure
            assert isinstance(market['dexRates'], list)
            assert len(market['dexRates']) == 2
            
            for rate in market['dexRates']:
                assert 'dex' in rate
                assert 'rate' in rate
                assert isinstance(rate['dex'], str)
                assert isinstance(rate['rate'], (int, float))
            
            # Check placeholder values
            assert market['volume24h'] == 0
            assert market['openInterest'] == 0
            assert market['lastUpdate'] == '2022-01-01T12:00:00'

    @pytest.mark.unit
    def test_combine_funding_data_dex_names(self):
        """Test that DEX names are correctly mapped."""
        dex_data = {
            'dydx': {'BTC': 87.6},
            'hyperliquid': {'BTC': 70.08},
            'paradex': {'BTC': 65.7},
            'extended': {'BTC': 61.32}
        }
        
        result = combine_funding_data(dex_data)
        
        btc_market = result[0]
        dex_names = [rate['dex'] for rate in btc_market['dexRates']]
        
        expected_names = ['dYdX', 'Hyperliquid', 'Paradex', 'Extended']
        for name in expected_names:
            assert name in dex_names

    @pytest.mark.unit
    def test_combine_funding_data_negative_rates(self):
        """Test handling of negative funding rates."""
        dex_data = {
            'dydx': {'SOL': -17.52},
            'hyperliquid': {'SOL': -8.76}
        }
        
        result = combine_funding_data(dex_data)
        
        sol_market = result[0]
        dex_rates = {rate['dex']: rate['rate'] for rate in sol_market['dexRates']}
        
        assert dex_rates['dYdX'] == -17.52
        assert dex_rates['Hyperliquid'] == -8.76

    @pytest.mark.unit
    def test_combine_funding_data_large_dataset(self):
        """Test combining data with many markets."""
        # Create large dataset
        markets = [f'TOKEN{i}' for i in range(100)]
        
        dex_data = {
            'dydx': {market: float(i) for i, market in enumerate(markets[:50])},
            'hyperliquid': {market: float(i + 0.5) for i, market in enumerate(markets[25:75])},
            'paradex': {market: float(i + 1.0) for i, market in enumerate(markets[40:90])},
            'extended': {market: float(i + 1.5) for i, market in enumerate(markets[60:])}
        }
        
        result = combine_funding_data(dex_data)
        
        # Should include markets that appear on at least 2 DEXs
        # Markets 25-49: dYdX + Hyperliquid (25 markets)
        # Markets 40-49: dYdX + Hyperliquid + Paradex (10 markets, already counted)
        # Markets 60-74: Hyperliquid + Paradex + Extended (15 markets)
        # Markets 75-89: Paradex + Extended (15 markets)
        # Total unique markets with 2+ DEXs should be significant
        
        assert len(result) > 0
        
        # All results should have at least 2 DEX rates
        for market in result:
            assert len(market['dexRates']) >= 2

    @pytest.mark.unit
    def test_combine_funding_data_zero_rates(self):
        """Test handling of zero funding rates."""
        dex_data = {
            'dydx': {'STABLE': 0.0},
            'hyperliquid': {'STABLE': 0.0}
        }
        
        result = combine_funding_data(dex_data)
        
        stable_market = result[0]
        dex_rates = {rate['dex']: rate['rate'] for rate in stable_market['dexRates']}
        
        assert dex_rates['dYdX'] == 0.0
        assert dex_rates['Hyperliquid'] == 0.0