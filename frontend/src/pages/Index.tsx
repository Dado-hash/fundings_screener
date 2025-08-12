
import { useState, useEffect } from 'react';
import { FundingRatesTable } from '../components/FundingRatesTable';
import { FundingRatesFilters } from '../components/FundingRatesFilters';
import { FundingRatesStats } from '../components/FundingRatesStats';
import { useFundingRates } from '../hooks/useFundingRates';
import { calculateMaxSpread, getOpportunityType } from '../utils/spreadCalculator';

const FILTERS_STORAGE_KEY = 'funding_rates_filters';

const Index = () => {
  const { data: fundingData, loading, isRefreshing, error, lastUpdate } = useFundingRates();
  const [filteredData, setFilteredData] = useState(fundingData);
  
  // Initialize filters from localStorage or defaults
  const [activeFilters, setActiveFilters] = useState(() => {
    const savedFilters = localStorage.getItem(FILTERS_STORAGE_KEY);
    if (savedFilters) {
      try {
        return JSON.parse(savedFilters);
      } catch (error) {
        console.warn('Error parsing saved filters:', error);
      }
    }
    return {
      showArbitrageOpportunities: false,
      showHighSpread: false,
      minSpread: 0,
      maxSpread: 500
    };
  });

  // Helper function to apply filters
  const applyFilters = (data: typeof fundingData, filters: typeof activeFilters) => {
    // Always start with data already filtered to exclude spread 0.0
    let filtered = data.filter(item => {
      const maxSpread = calculateMaxSpread(item.dexRates);
      return maxSpread.spread > 0;
    });
    
    if (filters.showArbitrageOpportunities) {
      filtered = filtered.filter(item => {
        const maxSpread = calculateMaxSpread(item.dexRates);
        return getOpportunityType(maxSpread) === 'arbitrage';
      });
    }
    
    if (filters.showHighSpread) {
      filtered = filtered.filter(item => {
        const maxSpread = calculateMaxSpread(item.dexRates);
        return maxSpread.spread >= 100;
      });
    }
    
    
    // Filter by spread range
    filtered = filtered.filter(item => {
      const maxSpread = calculateMaxSpread(item.dexRates);
      return maxSpread.spread >= filters.minSpread && maxSpread.spread <= filters.maxSpread;
    });
    
    return filtered;
  };

  // Update filtered data when funding data changes, preserving active filters
  useEffect(() => {
    const filtered = applyFilters(fundingData, activeFilters);
    setFilteredData(filtered);
  }, [fundingData, activeFilters]);

  const handleFilterChange = (filters: typeof activeFilters) => {
    setActiveFilters(filters);
    // Save filters to localStorage
    localStorage.setItem(FILTERS_STORAGE_KEY, JSON.stringify(filters));
    // The useEffect above will automatically update the filtered data
  };

  if (loading && fundingData.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-6 sm:mb-8">
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-slate-900 mb-2 px-2">
              <span className="hidden sm:inline">DeFi Perp Funding Rates - Maximum Spread Analysis</span>
              <span className="sm:hidden">DeFi Funding Rates</span>
            </h1>
            <p className="text-sm sm:text-base lg:text-lg text-slate-600 px-2">
              <span className="hidden sm:inline">
                Find the best arbitrage opportunities by automatically analyzing DEXs with the highest spread
              </span>
              <span className="sm:hidden">
                Arbitrage opportunities on DEXs
              </span>
            </p>
          </div>
          
          {/* Loading Skeletons */}
          <div className="space-y-4">
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="animate-pulse">
                <div className="h-6 bg-slate-200 rounded w-1/4 mb-4"></div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="h-16 bg-slate-200 rounded"></div>
                  <div className="h-16 bg-slate-200 rounded"></div>
                  <div className="h-16 bg-slate-200 rounded"></div>
                  <div className="h-16 bg-slate-200 rounded"></div>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="animate-pulse">
                <div className="h-6 bg-slate-200 rounded w-1/6 mb-4"></div>
                <div className="space-y-2">
                  <div className="h-4 bg-slate-200 rounded w-full"></div>
                  <div className="h-4 bg-slate-200 rounded w-3/4"></div>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-xl shadow-lg overflow-hidden">
              <div className="animate-pulse p-6">
                <div className="space-y-3">
                  <div className="h-12 bg-slate-200 rounded"></div>
                  <div className="h-12 bg-slate-100 rounded"></div>
                  <div className="h-12 bg-slate-200 rounded"></div>
                  <div className="h-12 bg-slate-100 rounded"></div>
                  <div className="h-12 bg-slate-200 rounded"></div>
                </div>
              </div>
            </div>
          </div>
          
          <div className="text-center mt-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
            <p className="text-sm text-slate-600">Loading funding rates...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-4 flex items-center justify-center">
        <div className="text-center bg-white rounded-xl shadow-lg p-8">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-slate-900 mb-2">Loading Error</h2>
          <p className="text-slate-600 mb-4">{error}</p>
          <p className="text-slate-500 text-sm">Data will be automatically updated every 3 minutes</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-2 sm:p-4">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-6 sm:mb-8">
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-slate-900 mb-2 px-2">
            <span className="hidden sm:inline">DeFi Perp Funding Rates - Maximum Spread Analysis</span>
            <span className="sm:hidden">DeFi Funding Rates</span>
          </h1>
          <p className="text-sm sm:text-base lg:text-lg text-slate-600 px-2">
            <span className="hidden sm:inline">
              Find the best arbitrage opportunities by automatically analyzing DEXs with the highest spread
            </span>
            <span className="sm:hidden">
              Arbitrage opportunities on DEXs
            </span>
          </p>
          {lastUpdate && (
            <div className="text-center mt-2 px-2">
              <p className="text-xs sm:text-sm text-slate-500 flex items-center justify-center gap-2">
                {isRefreshing && (
                  <div className="animate-spin rounded-full h-3 w-3 border-b border-blue-600"></div>
                )}
                <span className="font-medium">Last updated at:</span>
                {new Date(lastUpdate).toLocaleString('it-IT', {
                  day: '2-digit',
                  month: '2-digit', 
                  year: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                  second: '2-digit'
                })}
                {isRefreshing && (
                  <span className="text-blue-600 text-xs font-medium">(updating...)</span>
                )}
              </p>
            </div>
          )}
        </div>

        <FundingRatesStats data={fundingData} activeFilters={activeFilters} />
        
        <div className="bg-white rounded-xl shadow-lg p-4 sm:p-6 mb-4 sm:mb-6">
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3 mb-4">
            <h2 className="text-lg sm:text-xl font-semibold">Filters</h2>
            <div className="text-xs sm:text-sm text-slate-500 self-start sm:self-auto flex items-center gap-2">
              {isRefreshing && (
                <div className="animate-spin rounded-full h-3 w-3 border-b border-blue-600"></div>
              )}
              Automatic update every 10 minutes
              {lastUpdate && (
                <span className="text-slate-400">
                  • Last: {new Date(lastUpdate).toLocaleTimeString('it-IT')}
                </span>
              )}
            </div>
          </div>
          <FundingRatesFilters 
            filters={activeFilters}
            onFilterChange={handleFilterChange}
          />
        </div>

        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          <FundingRatesTable data={filteredData} />
        </div>
      </div>
    </div>
  );
};

export default Index;
