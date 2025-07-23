
import { useState } from 'react';
import { FundingRatesTable } from '../components/FundingRatesTable';
import { FundingRatesFilters } from '../components/FundingRatesFilters';
import { FundingRatesStats } from '../components/FundingRatesStats';
import { mockFundingData } from '../data/mockFundingData';
import { calculateMaxSpread, getOpportunityType } from '../utils/spreadCalculator';

const Index = () => {
  const [filteredData, setFilteredData] = useState(mockFundingData);
  const [activeFilters, setActiveFilters] = useState({
    showArbitrageOpportunities: false,
    showHighSpread: false,
    showLowSpread: false,
    minSpread: 0,
    maxSpread: 500
  });

  const handleFilterChange = (filters: typeof activeFilters) => {
    setActiveFilters(filters);
    
    let filtered = mockFundingData;
    
    if (filters.showArbitrageOpportunities) {
      filtered = filtered.filter(item => {
        const maxSpread = calculateMaxSpread(item.dexRates);
        return getOpportunityType(maxSpread) === 'arbitrage';
      });
    }
    
    if (filters.showHighSpread) {
      filtered = filtered.filter(item => {
        const maxSpread = calculateMaxSpread(item.dexRates);
        return getOpportunityType(maxSpread) === 'high-spread';
      });
    }
    
    if (filters.showLowSpread) {
      filtered = filtered.filter(item => {
        const maxSpread = calculateMaxSpread(item.dexRates);
        return getOpportunityType(maxSpread) === 'low-spread';
      });
    }
    
    // Filter by spread range
    filtered = filtered.filter(item => {
      const maxSpread = calculateMaxSpread(item.dexRates);
      return maxSpread.spread >= filters.minSpread && maxSpread.spread <= filters.maxSpread;
    });
    
    setFilteredData(filtered);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-4">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-slate-900 mb-2">
            DeFi Perp Funding Rates - Maximum Spread Analysis
          </h1>
          <p className="text-lg text-slate-600">
            Trova le migliori opportunità di arbitraggio analizzando automaticamente i DEX con il maggior spread
          </p>
        </div>

        <FundingRatesStats data={filteredData} />
        
        <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
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
