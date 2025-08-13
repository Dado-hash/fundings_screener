"""
Utility functions for the Telegram Bot
"""

import logging
import requests
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


async def fetch_funding_data(api_base_url: str) -> Optional[List[Dict[str, Any]]]:
    """
    Fetch funding rates data from the API
    
    Args:
        api_base_url: Base URL for the funding rates API
        
    Returns:
        List of funding rate data or None if error
    """
    try:
        url = f"{api_base_url}/funding-rates"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        return data.get('data', [])
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching funding data: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing funding data JSON: {e}")
        return None


def calculate_max_spread(dex_rates: List[Dict[str, Any]], selected_dexes: List[str]) -> Dict[str, Any]:
    """
    Calculate maximum spread for given DEX rates (replicates frontend logic)
    
    Args:
        dex_rates: List of dex rate objects with 'dex' and 'rate' keys
        selected_dexes: List of DEX names to include in calculation
        
    Returns:
        Dictionary with spread, high/low dex info
    """
    # Filter rates by selected DEXes
    filtered_rates = [rate for rate in dex_rates if rate['dex'] in selected_dexes]
    
    if len(filtered_rates) < 2:
        return {
            'spread': 0,
            'highDex': '',
            'lowDex': '', 
            'highRate': 0,
            'lowRate': 0
        }
    
    max_spread = 0
    high_dex = ''
    low_dex = ''
    high_rate = 0
    low_rate = 0
    
    # Compare all pairs to find maximum spread
    for i in range(len(filtered_rates)):
        for j in range(i + 1, len(filtered_rates)):
            spread = abs(filtered_rates[i]['rate'] - filtered_rates[j]['rate'])
            
            if spread > max_spread:
                max_spread = spread
                if filtered_rates[i]['rate'] > filtered_rates[j]['rate']:
                    high_dex = filtered_rates[i]['dex']
                    high_rate = filtered_rates[i]['rate'] 
                    low_dex = filtered_rates[j]['dex']
                    low_rate = filtered_rates[j]['rate']
                else:
                    high_dex = filtered_rates[j]['dex']
                    high_rate = filtered_rates[j]['rate']
                    low_dex = filtered_rates[i]['dex'] 
                    low_rate = filtered_rates[i]['rate']
    
    return {
        'spread': max_spread,
        'highDex': high_dex,
        'lowDex': low_dex,
        'highRate': high_rate,
        'lowRate': low_rate
    }


def get_opportunity_type(max_spread_result: Dict[str, Any]) -> str:
    """
    Determine opportunity type (replicates frontend logic)
    
    Args:
        max_spread_result: Result from calculate_max_spread
        
    Returns:
        'arbitrage', 'high-spread', or 'low-spread'
    """
    high_rate = max_spread_result.get('highRate', 0)
    low_rate = max_spread_result.get('lowRate', 0)
    spread = max_spread_result.get('spread', 0)
    
    # Arbitrage opportunity: opposite signs with significant spread
    if (high_rate > 0 and low_rate < 0) or (high_rate < 0 and low_rate > 0):
        return 'arbitrage'
    
    # High spread opportunity: same sign but significant difference
    if spread >= 100:
        return 'high-spread'
        
    return 'low-spread'


def apply_filters(funding_data: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Apply user filters to funding data (replicates frontend logic)
    
    Args:
        funding_data: Raw funding data from API
        filters: User filter settings
        
    Returns:
        Filtered list of opportunities
    """
    if not funding_data:
        return []
    
    selected_dexes = filters.get('selected_dexes', [])
    min_spread = filters.get('min_spread', 0)
    max_spread = filters.get('max_spread', 500)
    show_arbitrage_only = filters.get('show_arbitrage_only', False)
    show_high_spread_only = filters.get('show_high_spread_only', False)
    max_results = filters.get('max_results', 5)
    
    filtered = []
    
    for item in funding_data:
        # Calculate max spread for this market
        max_spread_result = calculate_max_spread(item['dexRates'], selected_dexes)
        
        # Skip if spread is 0 (not enough data)
        if max_spread_result['spread'] <= 0:
            continue
        
        # Apply spread range filter
        if not (min_spread <= max_spread_result['spread'] <= max_spread):
            continue
        
        # Apply opportunity type filters
        opportunity_type = get_opportunity_type(max_spread_result)
        
        if show_arbitrage_only and opportunity_type != 'arbitrage':
            continue
            
        if show_high_spread_only and max_spread_result['spread'] < 100:
            continue
        
        # Add to filtered results with calculated data
        filtered_item = {
            **item,
            'maxSpread': max_spread_result,
            'opportunityType': opportunity_type
        }
        filtered.append(filtered_item)
    
    # Sort by spread descending (best opportunities first)
    filtered.sort(key=lambda x: x['maxSpread']['spread'], reverse=True)
    
    # Limit results
    return filtered[:max_results]


def format_notification_message(opportunities: List[Dict[str, Any]], filters: Dict[str, Any]) -> str:
    """
    Format notification message for Telegram
    
    Args:
        opportunities: Filtered opportunities list
        filters: User filter settings
        
    Returns:
        Formatted message string
    """
    if not opportunities:
        return "📊 No opportunities found matching your criteria at this time."
    
    # Header
    alert_name = filters.get('name', 'Alert')
    dex_names = ', '.join(filters.get('selected_dexes', []))
    min_spread = int(filters.get('min_spread', 0))
    
    message = f"🚨 *{alert_name}* 🚨\n\n"
    message += f"📊 Found {len(opportunities)} opportunit{'y' if len(opportunities) == 1 else 'ies'}:\n\n"
    
    # Opportunities
    for i, opp in enumerate(opportunities, 1):
        market = opp['market']
        max_spread = opp['maxSpread']
        opp_type = opp['opportunityType']
        
        # Emoji based on opportunity type
        type_emoji = "🎯" if opp_type == 'arbitrage' else "📈" if opp_type == 'high-spread' else "📊"
        type_name = "Best Arbitrage" if opp_type == 'arbitrage' else "High Spread" if opp_type == 'high-spread' else "Opportunity"
        
        message += f"{i}️⃣ *{market}*\n"
        message += f"💰 Spread: *{max_spread['spread']:.1f} bps*\n"
        message += f"📈 {max_spread['highDex']}: +{max_spread['highRate']:.1f} bps\n"
        message += f"📉 {max_spread['lowDex']}: {max_spread['lowRate']:+.1f} bps\n"
        message += f"{type_emoji} {type_name}\n\n"
    
    # Footer
    current_time = datetime.now().strftime("%H:%M")
    
    # Handle both minutes and hours intervals
    if filters.get('interval_minutes'):
        next_check_time = filters['interval_minutes']
        time_unit = f"minute{'s' if next_check_time != 1 else ''}"
    else:
        next_check_time = filters.get('interval_hours', 5)
        time_unit = f"hour{'s' if next_check_time != 1 else ''}"
    
    message += f"⏰ Updated: {current_time}\n"
    message += f"🔄 Next check in {next_check_time} {time_unit}\n\n"
    message += "📱 Manage alerts: /alerts"
    
    return message


def format_rate(rate: float) -> str:
    """Format a funding rate with proper sign"""
    return f"{'+' if rate > 0 else ''}{rate:.1f}"


def validate_dex_list(dexes: List[str]) -> bool:
    """Validate that all DEXes are supported"""
    available_dexes = ['dYdX', 'Hyperliquid', 'Paradex', 'Extended']
    return all(dex in available_dexes for dex in dexes) and len(dexes) >= 2


def sanitize_alert_name(name: str) -> str:
    """Sanitize alert name for safe storage"""
    return name.strip()[:50]  # Max 50 chars


def validate_interval(hours: int) -> bool:
    """Validate notification interval"""
    return 1 <= hours <= 24


def validate_spread(spread: float) -> bool:
    """Validate spread threshold"""
    return 0 <= spread <= 1000