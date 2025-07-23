
export interface DexFundingRate {
  dex: string;
  rate: number; // in basis points (bps)
}

export interface FundingRateData {
  market: string;
  dexRates: DexFundingRate[];
  volume24h: number;
  openInterest: number;
  lastUpdate: string;
}

export interface MaxSpreadResult {
  spread: number;
  highDex: string;
  lowDex: string;
  highRate: number;
  lowRate: number;
}

export const mockFundingData: FundingRateData[] = [
  {
    market: 'ETH-USD',
    dexRates: [
      { dex: 'GMX', rate: 45.2 },
      { dex: 'dYdX', rate: -12.8 },
      { dex: 'Hyperliquid', rate: 78.5 },
      { dex: 'Vertex', rate: -23.1 }
    ],
    volume24h: 125000000,
    openInterest: 890000000,
    lastUpdate: '2024-01-15T10:30:00Z'
  },
  {
    market: 'BTC-USD',
    dexRates: [
      { dex: 'GMX', rate: 23.7 },
      { dex: 'dYdX', rate: 18.9 },
      { dex: 'Hyperliquid', rate: -45.6 },
      { dex: 'Vertex', rate: 67.8 }
    ],
    volume24h: 89000000,
    openInterest: 1200000000,
    lastUpdate: '2024-01-15T10:30:00Z'
  },
  {
    market: 'AVAX-USD',
    dexRates: [
      { dex: 'GMX', rate: -67.3 },
      { dex: 'dYdX', rate: 89.1 },
      { dex: 'Hyperliquid', rate: 12.4 },
      { dex: 'Gains Network', rate: -156.2 }
    ],
    volume24h: 45000000,
    openInterest: 78000000,
    lastUpdate: '2024-01-15T10:30:00Z'
  },
  {
    market: 'SOL-USD',
    dexRates: [
      { dex: 'GMX', rate: 156.8 },
      { dex: 'dYdX', rate: 12.4 },
      { dex: 'Hyperliquid', rate: -89.2 },
      { dex: 'Vertex', rate: 234.5 }
    ],
    volume24h: 67000000,
    openInterest: 145000000,
    lastUpdate: '2024-01-15T10:30:00Z'
  },
  {
    market: 'MATIC-USD',
    dexRates: [
      { dex: 'GMX', rate: -23.4 },
      { dex: 'dYdX', rate: -78.9 },
      { dex: 'Hyperliquid', rate: 45.6 },
      { dex: 'Gains Network', rate: 123.7 }
    ],
    volume24h: 23000000,
    openInterest: 56000000,
    lastUpdate: '2024-01-15T10:30:00Z'
  },
  {
    market: 'LINK-USD',
    dexRates: [
      { dex: 'GMX', rate: 34.6 },
      { dex: 'dYdX', rate: -89.2 },
      { dex: 'Hyperliquid', rate: 156.3 },
      { dex: 'Vertex', rate: -12.8 }
    ],
    volume24h: 34000000,
    openInterest: 89000000,
    lastUpdate: '2024-01-15T10:30:00Z'
  },
  {
    market: 'UNI-USD',
    dexRates: [
      { dex: 'GMX', rate: 8.7 },
      { dex: 'dYdX', rate: 11.3 },
      { dex: 'Hyperliquid', rate: -67.8 },
      { dex: 'Gains Network', rate: 89.4 }
    ],
    volume24h: 18000000,
    openInterest: 34000000,
    lastUpdate: '2024-01-15T10:30:00Z'
  },
  {
    market: 'AAVE-USD',
    dexRates: [
      { dex: 'GMX', rate: -145.7 },
      { dex: 'dYdX', rate: 67.8 },
      { dex: 'Hyperliquid', rate: 23.4 },
      { dex: 'Vertex', rate: -234.5 }
    ],
    volume24h: 12000000,
    openInterest: 23000000,
    lastUpdate: '2024-01-15T10:30:00Z'
  },
  {
    market: 'DOT-USD',
    dexRates: [
      { dex: 'GMX', rate: 78.9 },
      { dex: 'dYdX', rate: 45.2 },
      { dex: 'Hyperliquid', rate: -123.6 },
      { dex: 'Gains Network', rate: 12.7 }
    ],
    volume24h: 19000000,
    openInterest: 45000000,
    lastUpdate: '2024-01-15T10:30:00Z'
  },
  {
    market: 'ADA-USD',
    dexRates: [
      { dex: 'GMX', rate: -12.3 },
      { dex: 'dYdX', rate: 156.7 },
      { dex: 'Hyperliquid', rate: 34.5 },
      { dex: 'Vertex', rate: -89.1 }
    ],
    volume24h: 28000000,
    openInterest: 67000000,
    lastUpdate: '2024-01-15T10:30:00Z'
  }
];
