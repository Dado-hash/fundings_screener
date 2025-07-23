
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Filter, RotateCcw } from 'lucide-react';

interface FilterProps {
  showArbitrageOpportunities: boolean;
  showHighSpread: boolean;
  showLowSpread: boolean;
  minSpread: number;
  maxSpread: number;
}

interface FundingRatesFiltersProps {
  filters: FilterProps;
  onFilterChange: (filters: FilterProps) => void;
}

export const FundingRatesFilters = ({ filters, onFilterChange }: FundingRatesFiltersProps) => {
  const handleFilterToggle = (filterName: keyof FilterProps) => {
    onFilterChange({
      ...filters,
      [filterName]: !filters[filterName]
    });
  };

  const resetFilters = () => {
    onFilterChange({
      showArbitrageOpportunities: false,
      showHighSpread: false,
      showLowSpread: false,
      minSpread: 0,
      maxSpread: 500
    });
  };

  const getActiveFiltersCount = () => {
    return [filters.showArbitrageOpportunities, filters.showHighSpread, filters.showLowSpread].filter(Boolean).length;
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filtri Opportunità
            {getActiveFiltersCount() > 0 && (
              <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
                {getActiveFiltersCount()} attivi
              </span>
            )}
          </div>
          <Button variant="outline" size="sm" onClick={resetFilters}>
            <RotateCcw className="h-4 w-4 mr-2" />
            Reset
          </Button>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="flex items-center space-x-2">
            <Switch
              id="arbitrage-opportunities"
              checked={filters.showArbitrageOpportunities}
              onCheckedChange={() => handleFilterToggle('showArbitrageOpportunities')}
            />
            <Label htmlFor="arbitrage-opportunities" className="text-sm font-medium">
              Best Arbitrage
              <span className="block text-xs text-slate-500">
                Rates opposti con spread elevato
              </span>
            </Label>
          </div>

          <div className="flex items-center space-x-2">
            <Switch
              id="high-spread"
              checked={filters.showHighSpread}
              onCheckedChange={() => handleFilterToggle('showHighSpread')}
            />
            <Label htmlFor="high-spread" className="text-sm font-medium">
              High Spread
              <span className="block text-xs text-slate-500">
                Spread massimo &gt; 100 bps
              </span>
            </Label>
          </div>

          <div className="flex items-center space-x-2">
            <Switch
              id="low-spread"
              checked={filters.showLowSpread}
              onCheckedChange={() => handleFilterToggle('showLowSpread')}
            />
            <Label htmlFor="low-spread" className="text-sm font-medium">
              Low Spread
              <span className="block text-xs text-slate-500">
                Spread massimo &lt; 100 bps
              </span>
            </Label>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
