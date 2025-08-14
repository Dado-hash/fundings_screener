import { useState, useEffect, useRef } from 'react';
import { FundingRateData } from '../data/mockFundingData';

const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? '/api' 
  : 'http://localhost:5001/api';

const CACHE_KEY = 'funding_rates_cache';
const CACHE_TIMESTAMP_KEY = 'funding_rates_cache_timestamp';
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes - only for initial page load
const REFRESH_INTERVAL = 60 * 1000; // 60 seconds - background refresh to get new data

interface ApiResponse {
  data: FundingRateData[];
  lastUpdate: string;
  totalMarkets: number;
}

interface CacheData {
  data: FundingRateData[];
  lastUpdate: string;
  timestamp: number;
}

export const useFundingRates = () => {
  const [data, setData] = useState<FundingRateData[]>([]);
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<string | null>(null);
  const isFirstLoad = useRef(true);

  // Load data from localStorage cache
  const loadFromCache = (): CacheData | null => {
    try {
      const cachedData = localStorage.getItem(CACHE_KEY);
      const cachedTimestamp = localStorage.getItem(CACHE_TIMESTAMP_KEY);
      
      if (cachedData && cachedTimestamp) {
        const timestamp = parseInt(cachedTimestamp);
        const now = Date.now();
        
        // Always return cached data for immediate display
        const parsed: CacheData = JSON.parse(cachedData);
        return { ...parsed, timestamp };
      }
    } catch (err) {
      console.warn('Error loading from cache:', err);
    }
    return null;
  };

  // Save data to localStorage cache
  const saveToCache = (data: FundingRateData[], lastUpdate: string) => {
    try {
      const cacheData: CacheData = {
        data,
        lastUpdate,
        timestamp: Date.now()
      };
      localStorage.setItem(CACHE_KEY, JSON.stringify(cacheData));
      localStorage.setItem(CACHE_TIMESTAMP_KEY, Date.now().toString());
    } catch (err) {
      console.warn('Error saving to cache:', err);
    }
  };

  const fetchFundingRates = async (isBackgroundUpdate = false) => {
    try {
      // Only show loading spinner on first load
      if (isFirstLoad.current) {
        setLoading(true);
      } else if (!isBackgroundUpdate) {
        setIsRefreshing(true);
      }
      
      setError(null);
      
      const response = await fetch(`${API_BASE_URL}/funding-rates`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result: ApiResponse = await response.json();
      
      // Update state with fresh data
      setData(result.data);
      setLastUpdate(result.lastUpdate);
      
      // Cache the fresh data
      saveToCache(result.data, result.lastUpdate);
      
      isFirstLoad.current = false;
    } catch (err) {
      console.error('Error fetching funding rates:', err);
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    // First, try to load from cache for immediate display
    const cachedData = loadFromCache();
    if (cachedData) {
      setData(cachedData.data);
      setLastUpdate(cachedData.lastUpdate);
      setLoading(false);
      isFirstLoad.current = false;
      
      // Always fetch fresh data in background, regardless of cache age
      // The cache is just for immediate display
      fetchFundingRates(true);
    } else {
      // No cache, fetch fresh data with loading state
      fetchFundingRates();
    }
    
    // Background updates every 30 seconds (backend updates every 3 minutes)
    const interval = setInterval(() => {
      fetchFundingRates(true); // Background update
    }, REFRESH_INTERVAL);
    
    return () => clearInterval(interval);
  }, []);

  return {
    data,
    loading,
    isRefreshing,
    error,
    lastUpdate
  };
};