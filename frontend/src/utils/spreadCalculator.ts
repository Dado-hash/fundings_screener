
import { DexFundingRate, MaxSpreadResult } from '../data/mockFundingData';

export const calculateMaxSpread = (dexRates: DexFundingRate[]): MaxSpreadResult => {
  if (dexRates.length < 2) {
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
  for (let i = 0; i < dexRates.length; i++) {
    for (let j = i + 1; j < dexRates.length; j++) {
      const spread = Math.abs(dexRates[i].rate - dexRates[j].rate);
      
      if (spread > maxSpread) {
        maxSpread = spread;
        if (dexRates[i].rate > dexRates[j].rate) {
          highDex = dexRates[i].dex;
          highRate = dexRates[i].rate;
          lowDex = dexRates[j].dex;
          lowRate = dexRates[j].rate;
        } else {
          highDex = dexRates[j].dex;
          highRate = dexRates[j].rate;
          lowDex = dexRates[i].dex;
          lowRate = dexRates[i].rate;
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
