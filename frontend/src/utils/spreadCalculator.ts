
import { DexFundingRate, MaxSpreadResult } from '../data/mockFundingData';

export const calculateMaxSpread = (dexRates: DexFundingRate[], selectedDexes?: string[]): MaxSpreadResult => {
  // Filter rates by selected DEXes if provided
  const filteredRates = selectedDexes && selectedDexes.length > 0 
    ? dexRates.filter(rate => selectedDexes.includes(rate.dex))
    : dexRates;

  if (filteredRates.length < 2) {
    return {
      spread: 0,
      highDex: '',
      lowDex: '',
      highRate: 0,
      lowRate: 0
    };
  }

  let maxSpread = 0;
  let highDex = '';
  let lowDex = '';
  let highRate = 0;
  let lowRate = 0;

  // Compare all pairs to find the maximum spread
  for (let i = 0; i < filteredRates.length; i++) {
    for (let j = i + 1; j < filteredRates.length; j++) {
      const spread = Math.abs(filteredRates[i].rate - filteredRates[j].rate);
      
      if (spread > maxSpread) {
        maxSpread = spread;
        if (filteredRates[i].rate > filteredRates[j].rate) {
          highDex = filteredRates[i].dex;
          highRate = filteredRates[i].rate;
          lowDex = filteredRates[j].dex;
          lowRate = filteredRates[j].rate;
        } else {
          highDex = filteredRates[j].dex;
          highRate = filteredRates[j].rate;
          lowDex = filteredRates[i].dex;
          lowRate = filteredRates[i].rate;
        }
      }
    }
  }

  return {
    spread: maxSpread,
    highDex,
    lowDex,
    highRate,
    lowRate
  };
};

export const getOpportunityType = (maxSpread: MaxSpreadResult): 'arbitrage' | 'high-spread' | 'low-spread' => {
  const { highRate, lowRate, spread } = maxSpread;
  
  // Arbitrage opportunity: opposite signs with significant spread
  if ((highRate > 0 && lowRate < 0) || (highRate < 0 && lowRate > 0)) {
    return 'arbitrage';
  }
  
  // High spread opportunity: same sign but significant difference
  if (spread >= 100) {
    return 'high-spread';
  }
  
  return 'low-spread';
};
