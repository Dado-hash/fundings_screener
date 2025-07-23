
import { useState, useEffect } from 'react';
import { FundingRatesTable } from '../components/FundingRatesTable';
import { FundingRatesFilters } from '../components/FundingRatesFilters';
import { FundingRatesStats } from '../components/FundingRatesStats';
import { useFundingRates } from '../hooks/useFundingRates';
import { calculateMaxSpread, getOpportunityType } from '../utils/spreadCalculator';

const Index = () => {
  const { data: fundingData, loading, error, lastUpdate, refetch } = useFundingRates();
  const [filteredData, setFilteredData] = useState(fundingData);
  const [activeFilters, setActiveFilters] = useState({
    showArbitrageOpportunities: false,
    showHighSpread: false,
    showLowSpread: false,
    minSpread: 0,
    maxSpread: 500
  });

  // Update filtered data when funding data changes
  useEffect(() => {
    setFilteredData(fundingData);
  }, [fundingData]);

  const handleFilterChange = (filters: typeof activeFilters) => {
    setActiveFilters(filters);
    
    let filtered = fundingData;
    
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

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-4 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-lg text-slate-600">Caricamento funding rates...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-4 flex items-center justify-center">
        <div className="text-center bg-white rounded-xl shadow-lg p-8">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-slate-900 mb-2">Errore nel caricamento</h2>
          <p className="text-slate-600 mb-4">{error}</p>
          <button 
            onClick={refetch}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Riprova
          </button>
        </div>
      </div>
    );
  }

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
          {lastUpdate && (
            <p className="text-sm text-slate-500 mt-2">
              Ultimo aggiornamento: {new Date(lastUpdate).toLocaleString('it-IT')}
            </p>
          )}
        </div>

        <FundingRatesStats data={filteredData} />
        
        <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Filtri</h2>
            <button 
              onClick={refetch}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm"
            >
              Aggiorna Dati
            </button>
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
