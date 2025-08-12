
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowUpDown, TrendingUp, TrendingDown } from '@/lib/icons';
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
        <CardTitle className="flex items-center gap-2 text-lg md:text-xl">
          <ArrowUpDown className="h-5 w-5" />
          <span className="hidden sm:inline">Funding Rates Comparison - Maximum Spread Analysis</span>
          <span className="sm:hidden">Funding Rates</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* Desktop Table View */}
        <div className="hidden lg:block overflow-x-auto">
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

        {/* Mobile Card View */}
        <div className="lg:hidden space-y-4">
          {data.map((item, index) => {
            const maxSpread = calculateMaxSpread(item.dexRates);
            return (
              <Card key={index} className="border-2 hover:shadow-md transition-shadow">
                <CardContent className="p-4">
                  {/* Header with Market and Opportunity */}
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-bold text-slate-900">{item.market}</h3>
                    {getOpportunityIndicator(maxSpread)}
                  </div>

                  {/* Max Spread - Prominent Display */}
                  <div className="bg-slate-100 rounded-lg p-3 mb-4 text-center">
                    <div className="text-sm text-slate-600 mb-1">Max Spread</div>
                    <div className="text-2xl font-bold text-slate-900">
                      {maxSpread.spread.toFixed(1)} <span className="text-lg font-normal text-slate-600">bps</span>
                    </div>
                  </div>

                  {/* Best Pair */}
                  <div className="mb-4">
                    <div className="text-sm font-medium text-slate-700 mb-2">Best Arbitrage Pair:</div>
                    <div className="flex items-center justify-center space-x-2 text-sm">
                      <span className="font-medium text-green-600 bg-green-50 px-2 py-1 rounded">
                        {maxSpread.highDex}: {formatRate(maxSpread.highRate)}
                      </span>
                      <ArrowUpDown className="h-4 w-4 text-slate-400" />
                      <span className="font-medium text-red-600 bg-red-50 px-2 py-1 rounded">
                        {maxSpread.lowDex}: {formatRate(maxSpread.lowRate)}
                      </span>
                    </div>
                  </div>

                  {/* All DEX Rates */}
                  <div>
                    <div className="text-sm font-medium text-slate-700 mb-2">All DEX Rates:</div>
                    <div className="grid grid-cols-2 gap-2">
                      {item.dexRates.map((dexRate, dexIndex) => {
                        const isMaxSpreadDex = dexRate.dex === maxSpread.highDex || dexRate.dex === maxSpread.lowDex;
                        return (
                          <div
                            key={dexIndex}
                            className={`flex items-center justify-between p-2 rounded text-sm ${
                              isMaxSpreadDex 
                                ? `${getRateColor(dexRate.rate)} ring-2 ring-blue-400` 
                                : `${getRateColor(dexRate.rate)} opacity-60`
                            }`}
                          >
                            <span className="font-medium">{dexRate.dex}</span>
                            <div className="flex items-center">
                              {dexRate.rate > 0 ? <TrendingUp className="h-3 w-3 mr-1" /> : <TrendingDown className="h-3 w-3 mr-1" />}
                              <span className="font-semibold">{formatRate(dexRate.rate)}</span>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};
