
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
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Best Arbitrage</CardTitle>
          <ArrowUpDown className="h-4 w-4 text-blue-600" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-blue-600">{stats.arbitrageOpportunities}</div>
          <p className="text-xs text-muted-foreground">
            Opportunità di arbitraggio
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">High Spread</CardTitle>
          <TrendingUp className="h-4 w-4 text-yellow-600" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-yellow-600">{stats.highSpreadOpportunities}</div>
          <p className="text-xs text-muted-foreground">
            Spread elevati disponibili
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Avg Max Spread</CardTitle>
          <TrendingDown className="h-4 w-4 text-purple-600" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-purple-600">{stats.avgMaxSpread.toFixed(1)}</div>
          <p className="text-xs text-muted-foreground">
            Media spread massimi (bps)
          </p>
        </CardContent>
      </Card>
    </div>
  );
};
