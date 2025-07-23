
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowUpDown, TrendingUp, TrendingDown } from 'lucide-react';
import { FundingRateData } from '../data/mockFundingData';
import { calculateMaxSpread, getOpportunityType } from '../utils/spreadCalculator';

interface FundingRatesTableProps {
  data: FundingRateData[];
}

export const FundingRatesTable = ({ data }: FundingRatesTableProps) => {
  const formatRate = (rate: number) => {
    return `${rate > 0 ? '+' : ''}${rate.toFixed(1)}`;
  };

  const getRateColor = (rate: number) => {
    if (rate > 0) return 'text-green-600 bg-green-50';
    if (rate < 0) return 'text-red-600 bg-red-50';
    return 'text-gray-600 bg-gray-50';
  };

  const getOpportunityIndicator = (maxSpread: ReturnType<typeof calculateMaxSpread>) => {
    const opportunityType = getOpportunityType(maxSpread);
    
    switch (opportunityType) {
      case 'arbitrage':
        return <Badge variant="destructive" className="bg-blue-100 text-blue-800">Best Arbitrage</Badge>;
      case 'high-spread':
        return <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">High Spread</Badge>;
      default:
        return <Badge variant="outline" className="bg-gray-100 text-gray-600">Low Spread</Badge>;
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <ArrowUpDown className="h-5 w-5" />
          Funding Rates Comparison - Maximum Spread Analysis
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left p-4 font-semibold">Market</th>
                <th className="text-center p-4 font-semibold">All DEXs</th>
                <th className="text-center p-4 font-semibold">Max Spread</th>
                <th className="text-center p-4 font-semibold">Best Pair</th>
                <th className="text-center p-4 font-semibold">Opportunity</th>
              </tr>
            </thead>
            <tbody>
              {data.map((item, index) => {
                const maxSpread = calculateMaxSpread(item.dexRates);
                return (
                  <tr key={index} className="border-b hover:bg-slate-50 transition-colors">
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        <div className="font-semibold text-slate-900">{item.market}</div>
                      </div>
                    </td>
                    <td className="p-4">
                      <div className="flex flex-wrap gap-1 justify-center">
                        {item.dexRates.map((dexRate, dexIndex) => {
                          const isMaxSpreadDex = dexRate.dex === maxSpread.highDex || dexRate.dex === maxSpread.lowDex;
                          return (
                            <div
                              key={dexIndex}
                              className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${
                                isMaxSpreadDex 
                                  ? `${getRateColor(dexRate.rate)} ring-2 ring-blue-400` 
                                  : `${getRateColor(dexRate.rate)} opacity-60`
                              }`}
                            >
                              <span className="font-semibold mr-1">{dexRate.dex}:</span>
                              {dexRate.rate > 0 ? <TrendingUp className="h-3 w-3 mr-1" /> : <TrendingDown className="h-3 w-3 mr-1" />}
                              {formatRate(dexRate.rate)}
                            </div>
                          );
                        })}
                      </div>
                    </td>
                    <td className="p-4 text-center">
                      <div className="text-lg font-bold text-slate-900">
                        {maxSpread.spread.toFixed(1)} <span className="text-sm font-normal text-slate-600">bps</span>
                      </div>
                    </td>
                    <td className="p-4 text-center">
                      <div className="space-y-1">
                        <div className="text-sm">
                          <span className="font-medium text-green-600">{maxSpread.highDex}</span>
                          <span className="text-slate-500 mx-1">vs</span>
                          <span className="font-medium text-red-600">{maxSpread.lowDex}</span>
                        </div>
                        <div className="text-xs text-slate-500">
                          {formatRate(maxSpread.highRate)} → {formatRate(maxSpread.lowRate)}
                        </div>
                      </div>
                    </td>
                    <td className="p-4 text-center">
                      {getOpportunityIndicator(maxSpread)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
};
