
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { TrendingUp, TrendingDown, ArrowUpDown } from '@/lib/icons';
import { FundingRateData } from '../data/mockFundingData';
import { calculateMaxSpread, getOpportunityType } from '../utils/spreadCalculator';

interface FundingRatesStatsProps {
  data: FundingRateData[];
  activeFilters: {
    showArbitrageOpportunities: boolean;
    showHighSpread: boolean;
    selectedDexes: string[];
    minSpread: number;
    maxSpread: number;
  };
}

export const FundingRatesStats = ({ data, activeFilters }: FundingRatesStatsProps) => {
  const getStats = () => {
    const opportunities = data.map(item => {
      const selectedDexes = activeFilters.selectedDexes || ['dYdX', 'Hyperliquid', 'Paradex', 'Extended'];
      const maxSpread = calculateMaxSpread(item.dexRates, selectedDexes);
      return {
        ...item,
        maxSpread,
        opportunityType: getOpportunityType(maxSpread)
      };
    });

    const arbitrageOpportunities = opportunities.filter(item => item.opportunityType === 'arbitrage').length;
    const highSpreadOpportunities = opportunities.filter(item => item.maxSpread.spread >= 100).length;
    const avgMaxSpread = opportunities.reduce((sum, item) => sum + item.maxSpread.spread, 0) / opportunities.length;

    return {
      arbitrageOpportunities,
      highSpreadOpportunities,
      avgMaxSpread
    };
  };

  const stats = getStats();

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
      <Card className={`transition-all ${
        activeFilters.showArbitrageOpportunities 
          ? 'shadow-md shadow-blue-100 ring-2 ring-blue-200 bg-blue-50/30' 
          : 'hover:shadow-md'
      }`}>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
          <CardTitle className="text-sm font-medium text-slate-700">Best Arbitrage</CardTitle>
          <div className="p-2 bg-blue-100 rounded-full">
            <ArrowUpDown className="h-4 w-4 text-blue-600" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold text-blue-600 mb-1">{stats.arbitrageOpportunities}</div>
          <p className="text-sm text-slate-600">
            Arbitrage opportunities
          </p>
        </CardContent>
      </Card>

      <Card className={`transition-all ${
        activeFilters.showHighSpread 
          ? 'shadow-md shadow-orange-100 ring-2 ring-orange-200 bg-orange-50/30' 
          : 'hover:shadow-md'
      }`}>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
          <CardTitle className="text-sm font-medium text-slate-700">Spread ≥100 bps</CardTitle>
          <div className="p-2 bg-orange-100 rounded-full">
            <TrendingUp className="h-4 w-4 text-orange-600" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold text-orange-600 mb-1">{stats.highSpreadOpportunities}</div>
          <p className="text-sm text-slate-600">
            Markets with spread ≥100 bps
          </p>
        </CardContent>
      </Card>

      <Card className="hover:shadow-md transition-all sm:col-span-2 lg:col-span-1">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
          <CardTitle className="text-sm font-medium text-slate-700">Avg Max Spread</CardTitle>
          <div className="p-2 bg-purple-100 rounded-full">
            <TrendingDown className="h-4 w-4 text-purple-600" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold text-purple-600 mb-1">
            {stats.avgMaxSpread.toFixed(1)}
            <span className="text-lg font-normal text-slate-500 ml-1">bps</span>
          </div>
          <p className="text-sm text-slate-600">
            Average max spreads
          </p>
        </CardContent>
      </Card>
    </div>
  );
};
