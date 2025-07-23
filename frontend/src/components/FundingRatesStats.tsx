
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { TrendingUp, TrendingDown, ArrowUpDown } from 'lucide-react';
import { FundingRateData } from '../data/mockFundingData';
import { calculateMaxSpread, getOpportunityType } from '../utils/spreadCalculator';

interface FundingRatesStatsProps {
  data: FundingRateData[];
}

export const FundingRatesStats = ({ data }: FundingRatesStatsProps) => {
  const getStats = () => {
    const opportunities = data.map(item => {
      const maxSpread = calculateMaxSpread(item.dexRates);
      return {
        ...item,
        maxSpread,
        opportunityType: getOpportunityType(maxSpread)
      };
    });

    const arbitrageOpportunities = opportunities.filter(item => item.opportunityType === 'arbitrage').length;
    const highSpreadOpportunities = opportunities.filter(item => item.opportunityType === 'high-spread').length;
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
      <Card className="hover:shadow-md transition-shadow">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
          <CardTitle className="text-sm font-medium text-slate-700">Best Arbitrage</CardTitle>
          <div className="p-2 bg-blue-100 rounded-full">
            <ArrowUpDown className="h-4 w-4 text-blue-600" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold text-blue-600 mb-1">{stats.arbitrageOpportunities}</div>
          <p className="text-sm text-slate-600">
            Opportunità di arbitraggio
          </p>
          <div className="mt-2 w-full bg-slate-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
              style={{ width: `${Math.min((stats.arbitrageOpportunities / data.length) * 100, 100)}%` }}
            ></div>
          </div>
        </CardContent>
      </Card>

      <Card className="hover:shadow-md transition-shadow">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
          <CardTitle className="text-sm font-medium text-slate-700">High Spread</CardTitle>
          <div className="p-2 bg-yellow-100 rounded-full">
            <TrendingUp className="h-4 w-4 text-yellow-600" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold text-yellow-600 mb-1">{stats.highSpreadOpportunities}</div>
          <p className="text-sm text-slate-600">
            Spread elevati disponibili
          </p>
          <div className="mt-2 w-full bg-slate-200 rounded-full h-2">
            <div 
              className="bg-yellow-600 h-2 rounded-full transition-all duration-300" 
              style={{ width: `${Math.min((stats.highSpreadOpportunities / data.length) * 100, 100)}%` }}
            ></div>
          </div>
        </CardContent>
      </Card>

      <Card className="hover:shadow-md transition-shadow sm:col-span-2 lg:col-span-1">
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
            Media spread massimi
          </p>
          <div className="mt-2 flex items-center text-xs text-slate-500">
            <span className="mr-2">Range:</span>
            <div className="flex-1 bg-slate-200 rounded-full h-1.5">
              <div 
                className="bg-purple-600 h-1.5 rounded-full" 
                style={{ width: `${Math.min((stats.avgMaxSpread / 500) * 100, 100)}%` }}
              ></div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
