import { useState, useEffect } from 'react';
import { FundingRateData } from '../data/mockFundingData';

const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? '/api' 
  : 'http://localhost:5000/api';

interface ApiResponse {
  data: FundingRateData[];
  lastUpdate: string;
  totalMarkets: number;
}

export const useFundingRates = () => {
  const [data, setData] = useState<FundingRateData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<string | null>(null);

  const fetchFundingRates = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${API_BASE_URL}/funding-rates`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result: ApiResponse = await response.json();
      
      setData(result.data);
      setLastUpdate(result.lastUpdate);
    } catch (err) {
      console.error('Error fetching funding rates:', err);
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFundingRates();
    
    // Refresh data every 5 minutes
    const interval = setInterval(fetchFundingRates, 5 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, []);

  const refetch = () => {
    fetchFundingRates();
  };

  return {
    data,
    loading,
    error,
    lastUpdate,
    refetch
  };
};