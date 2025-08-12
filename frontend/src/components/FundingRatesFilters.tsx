
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Filter, RotateCcw } from '@/lib/icons';

// Available DEX names from the backend API
export const AVAILABLE_DEXES = ['dYdX', 'Hyperliquid', 'Paradex', 'Extended'] as const;

interface FilterProps {
  showArbitrageOpportunities: boolean;
  showHighSpread: boolean;
  selectedDexes: string[];
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

  const handleDexToggle = (dexName: string) => {
    const currentSelectedDexes = filters.selectedDexes || [...AVAILABLE_DEXES];
    const newSelectedDexes = currentSelectedDexes.includes(dexName)
      ? currentSelectedDexes.filter(d => d !== dexName)
      : [...currentSelectedDexes, dexName];
    
    onFilterChange({
      ...filters,
      selectedDexes: newSelectedDexes
    });
  };

  const handleSelectAllDexes = () => {
    onFilterChange({
      ...filters,
      selectedDexes: [...AVAILABLE_DEXES]
    });
  };

  const handleDeselectAllDexes = () => {
    onFilterChange({
      ...filters,
      selectedDexes: []
    });
  };

  const resetFilters = () => {
    onFilterChange({
      showArbitrageOpportunities: false,
      showHighSpread: false,
      selectedDexes: [...AVAILABLE_DEXES],
      minSpread: 0,
      maxSpread: 500
    });
  };

  const getActiveFiltersCount = () => {
    const opportunityFilters = [filters.showArbitrageOpportunities, filters.showHighSpread].filter(Boolean).length;
    const selectedDexes = filters.selectedDexes || [];
    const isDexFiltered = selectedDexes.length < AVAILABLE_DEXES.length;
    return opportunityFilters + (isDexFiltered ? 1 : 0);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            <span className="text-base sm:text-lg">Opportunity Filters</span>
            {getActiveFiltersCount() > 0 && (
              <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
                {getActiveFiltersCount()} active
              </span>
            )}
          </div>
          <Button variant="outline" size="sm" onClick={resetFilters} className="self-start">
            <RotateCcw className="h-4 w-4 mr-2" />
            Reset
          </Button>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
          <div className="flex items-start space-x-3 p-3 rounded-lg border border-slate-200 hover:bg-slate-50 transition-colors">
            <Switch
              id="arbitrage-opportunities"
              checked={filters.showArbitrageOpportunities}
              onCheckedChange={() => handleFilterToggle('showArbitrageOpportunities')}
              className="mt-1"
            />
            <Label htmlFor="arbitrage-opportunities" className="text-sm font-medium cursor-pointer flex-1">
              <div className="font-semibold text-slate-900">Best Arbitrage</div>
              <div className="text-xs text-slate-500 mt-1">
                Opportunities with opposite rates and high spread
              </div>
            </Label>
          </div>

          <div className="flex items-start space-x-3 p-3 rounded-lg border border-slate-200 hover:bg-slate-50 transition-colors">
            <Switch
              id="high-spread"
              checked={filters.showHighSpread}
              onCheckedChange={() => handleFilterToggle('showHighSpread')}
              className="mt-1"
            />
            <Label htmlFor="high-spread" className="text-sm font-medium cursor-pointer flex-1">
              <div className="font-semibold text-slate-900">Spread ≥100 bps</div>
              <div className="text-xs text-slate-500 mt-1">
                Maximum spread 100 bps or greater
              </div>
            </Label>
          </div>
        </div>

        {/* DEX Selection */}
        <div className="mt-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-medium text-slate-900">DEX Selection</h3>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleSelectAllDexes}
                className="text-xs"
              >
                All
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleDeselectAllDexes}
                className="text-xs"
              >
                None
              </Button>
            </div>
          </div>
          
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {AVAILABLE_DEXES.map((dex) => (
              <div key={dex} className="flex items-center space-x-2 p-2 rounded-lg border border-slate-200 hover:bg-slate-50 transition-colors">
                <Switch
                  id={`dex-${dex.toLowerCase()}`}
                  checked={(filters.selectedDexes || []).includes(dex)}
                  onCheckedChange={() => handleDexToggle(dex)}
                  className="scale-75"
                />
                <Label htmlFor={`dex-${dex.toLowerCase()}`} className="text-sm font-medium cursor-pointer flex-1">
                  {dex}
                </Label>
              </div>
            ))}
          </div>

          {(filters.selectedDexes || []).length < 2 && (
            <div className="mt-3 p-3 bg-amber-50 border border-amber-200 rounded-lg">
              <p className="text-sm text-amber-800">
                ⚠️ Select at least 2 DEXes to calculate meaningful spreads
              </p>
            </div>
          )}

          <div className="mt-2 text-xs text-slate-500">
            {(filters.selectedDexes || []).length} of {AVAILABLE_DEXES.length} DEXes selected
          </div>
        </div>
        
        {/* Active Filters Summary - Mobile */}
        {getActiveFiltersCount() > 0 && (
          <div className="mt-4 p-3 bg-blue-50 rounded-lg sm:hidden">
            <div className="text-sm font-medium text-blue-900 mb-2">Active Filters:</div>
            <div className="flex flex-wrap gap-2">
              {filters.showArbitrageOpportunities && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  Best Arbitrage
                </span>
              )}
              {filters.showHighSpread && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                  Spread ≥100 bps
                </span>
              )}
              {(filters.selectedDexes || []).length < AVAILABLE_DEXES.length && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  {(filters.selectedDexes || []).length}/{AVAILABLE_DEXES.length} DEXes
                </span>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
